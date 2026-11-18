"""Markdown → Typst 标记转换。

只负责把一章正文转成 Typst 标记，不负责书籍骨架（封面、目录、分页），
那是 build.py 的事。标题按 Markdown 层级原样映射（H2→三级），不做层级补偿。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

from markdown_it import MarkdownIt

# Typst 标记里需要反斜杠转义的字符
_SPECIAL = set("\\#$*_`<>@~[]/")

# 图题注：*图 4-1：从需求到结构的设计翻译链*
CAPTION_RE = re.compile(r"^(图|表|例)\s*\d+-\d+[：:].*$")

# 代码说明行：**代码 5-1-5** · 命令（Bash）
CODE_CAPTION_RE = re.compile(r"^代码\s*\d+-\d+-\d+")

# 勾选式条目：- [ ] / - [x]（转义后为 \[ \]）
_TASK_RE = re.compile(r"^\\\[([ x])\\\] (.*)$")

# 超过这个行数的代码块允许跨页，否则整块挪到下一页
CODE_GROUP_BREAK_LINES = 12

_md = MarkdownIt("commonmark").enable(["table", "strikethrough"])

# 当前转换使用的 mermaid 解析器（由 convert 设置，块级渲染时读取）
_RESOLVER: Callable[[str], str] | None = None

# 当前所在的编号小节（如 "8.1"）与小标题计数，用于给节内小标题编号
_CTX = {"section": None, "pseudo": 0}

_SECTION_RE = re.compile(r"^(\d+\.\d+)\s")


def escape(text: str) -> str:
    """转义 Typst 标记特殊字符，使文本按字面显示。"""
    return "".join("\\" + ch if ch in _SPECIAL else ch for ch in text)


def code_span(text: str) -> str:
    """行内代码：内容含反引号时用更长的反引号串包裹。"""
    text = text.replace("\n", " ")
    ticks = "`"
    while ticks in text:
        ticks += "`"
    return f"{ticks}{text}{ticks}"


def _render_children(children) -> str:
    out: list[str] = []
    link_stack: list[bool] = []
    for child in children:
        kind = child.type
        if kind == "text":
            out.append(escape(child.content))
        elif kind == "code_inline":
            out.append(code_span(child.content))
        elif kind in ("strong_open", "strong_close"):
            out.append("*")
        elif kind in ("em_open", "em_close"):
            out.append("_")
        elif kind == "s_open":
            out.append("#strike[")
        elif kind == "s_close":
            out.append("]")
        elif kind == "softbreak":
            out.append("\n")
        elif kind == "hardbreak":
            out.append("\\\n")
        elif kind == "link_open":
            href = child.attrGet("href") or ""
            external = href.startswith(("http://", "https://"))
            link_stack.append(external)
            if external:
                out.append(f'#link("{href}")[')
        elif kind == "link_close":
            if link_stack and link_stack.pop():
                out.append("]")
        elif kind == "image":
            out.append(escape(child.content or ""))
        elif kind == "html_inline":
            continue
        else:
            out.append(escape(child.content))
    return "".join(out)


def _render_inline(token) -> str:
    return _render_children(token.children or [])


def _meaningful(children) -> list:
    """去掉 markdown-it 在行首行尾插入的空 text token。"""
    return [
        child
        for child in (children or [])
        if not (child.type == "text" and child.content == "")
    ]


def _plain_inline(token) -> str:
    return "".join(child.content for child in (token.children or []) if child.type == "text")


def _is_pseudo_heading(inline) -> bool:
    """整段只有一个加粗 run 才算伪标题；句中夹带加粗的普通段落不算。

    加粗 run 内部可以含行内代码、强调等（如「用 `Depends` 注入查询参数」），
    只要第一个加粗的闭合就是整段末尾。
    """
    children = _meaningful(inline.children)
    if len(children) < 3 or children[0].type != "strong_open":
        return False
    depth = 0
    for index, child in enumerate(children):
        if child.type == "strong_open":
            depth += 1
        elif child.type == "strong_close":
            depth -= 1
            if depth == 0:
                return index == len(children) - 1
    return False


def _is_caption(inline) -> bool:
    children = _meaningful(inline.children)
    return (
        len(children) == 3
        and children[0].type == "em_open"
        and children[1].type == "text"
        and children[2].type == "em_close"
        and bool(CAPTION_RE.match(children[1].content.strip()))
    )


def _guard_line_start(text: str) -> str:
    """行首的 - + = / 会被 Typst 当成列表、标题或注释，前面补转义。"""
    if text[:1] in "-+=/":
        return "\\" + text
    return text


def _align_of(token) -> str:
    style = token.attrGet("style") or ""
    match = re.search(r"text-align:\s*(left|right|center)", style)
    return match.group(1) if match else "left"


def _render_list(tokens, i: int, depth: int, offset: int) -> tuple[int, str]:
    open_token = tokens[i]
    ordered = open_token.type == "ordered_list_open"
    close_type = "ordered_list_close" if ordered else "bullet_list_close"
    marker = "+" if ordered else "-"
    i += 1

    items: list[list[str]] = []
    while tokens[i].type != close_type:
        if tokens[i].type != "list_item_open":
            i += 1
            continue
        i += 1
        content: list[str] = []
        while tokens[i].type != "list_item_close":
            i, block = _render_block(tokens, i, depth + 1, offset)
            if block:
                content.append(block)
        i += 1
        items.append(content)
    i += 1

    indent = "  " * depth
    bodies = []
    task_items = 0
    for content in items:
        body = "\n\n".join(content) if content else ""
        body = body.replace("\n", "\n" + "  " * (depth + 1))
        match = _TASK_RE.match(body)
        if match:
            task_items += 1
            body = match.group(2).strip() + body[match.end():]
            body = ("■ " if match.group(1) == "x" else "□ ") + body
        bodies.append(body)

    lines = [f"{indent}{marker} {body}" for body in bodies]
    text = "\n".join(lines)
    # 全部条目都是勾选框时，去掉项目符号，只留方框
    if items and task_items == len(items) and depth == 0:
        return i, "#task-list[\n" + text + "\n]"
    return i, text


def _render_blockquote(tokens, i: int, depth: int, offset: int) -> tuple[int, str]:
    i += 1
    parts: list[str] = []
    while tokens[i].type != "blockquote_close":
        i, block = _render_block(tokens, i, depth, offset)
        if block:
            parts.append(block)
    i += 1
    body = "\n\n".join(parts).replace("💡", "").strip()
    return i, "#callout[\n" + body + "\n]"


def _display_width(text: str) -> int:
    """估算单元格显示宽度：中日韩字符按 2 计，标记符号不计。"""
    width = 0
    for ch in text:
        if ch in r"\*_`":
            continue
        width += 2 if ord(ch) > 0x2E80 else 1
    return width


def _column_widths(rows: list[list[str]], ncols: int) -> list[int]:
    widths = []
    for col in range(ncols):
        widest = max(
            (_display_width(row[col]) for row in rows if col < len(row)),
            default=4,
        )
        widths.append(max(widest, 4))
    return widths


def _render_table(tokens, i: int) -> tuple[int, str]:
    i += 1
    rows: list[list[str]] = []
    current: list[str] | None = None
    aligns: list[str] = []

    while tokens[i].type != "table_close":
        token = tokens[i]
        if token.type == "tr_open":
            current = []
            i += 1
        elif token.type == "tr_close":
            if current is not None:
                rows.append(current)
            current = None
            i += 1
        elif token.type in ("th_open", "td_open"):
            if token.type == "th_open" and len(aligns) < len(current or []) + 1:
                aligns.append(_align_of(token))
            if current is not None:
                current.append(_render_inline(tokens[i + 1]))
            i += 3
        else:
            i += 1
    i += 1

    if not rows:
        return i, ""
    ncols = max(len(row) for row in rows)
    while len(aligns) < ncols:
        aligns.append("left")
    header, body = rows[0], rows[1:]

    # 列宽按内容宽度开方压缩，并保证每列不低于 9%，避免窄列被挤成逐字换行
    raw = _column_widths(rows, ncols)
    weights = [width ** 0.6 for width in raw]
    total = sum(weights)
    shares = [max(weight / total, 0.09) for weight in weights]
    scale = sum(shares) / 1.0
    shares = [share / scale for share in shares]
    columns = "(" + ", ".join(f"{share:.3f}fr" for share in shares) + ")"
    lines = [
        "#table(",
        f"  columns: {columns},",
        f"  align: ({', '.join(aligns[:ncols])}),",
        "  stroke: none,",
        "  table.hline(stroke: 1pt),",
    ]
    lines.append("  table.header(" + ", ".join(f"[{cell}]" for cell in header) + "),")
    lines.append("  table.hline(stroke: 0.5pt),")
    for row in body:
        cells = row + [""] * (ncols - len(row))
        lines.append("  " + ", ".join(f"[{cell}]" for cell in cells) + ",")
    lines.append("  table.hline(stroke: 1pt),")
    lines.append(")")
    return i, "\n".join(lines)


def _render_code(token) -> str:
    info = (token.info or "").strip()
    lang = info.split()[0] if info else ""
    # 超长行交给 Typst 在词边界自动换行：手工按列切会切断标识符
    body = token.content.rstrip("\n")
    ticks = "```"
    while ticks in body or ticks + lang in body:
        ticks += "`"
    return f"{ticks}{lang}\n{body}\n{ticks}"


def _code_group(code_markup: str, token, caption: str | None = None) -> str:
    """把代码说明行与代码块绑成一个整体，避免题注落在页底、代码被挤到下一页。"""
    lines = token.content.rstrip("\n").count("\n") + 1
    long_block = "true" if lines > CODE_GROUP_BREAK_LINES else "false"
    parts = []
    if caption is not None:
        parts.append("#code-caption[" + caption + "]")
    parts.append(code_markup)
    inner = "\n\n".join(parts)
    return f"#code-group(long: {long_block})[\n{inner}\n]"


def _render_mermaid(token) -> str:
    info = _RESOLVER(token.content.strip("\n")) if _RESOLVER else None
    if not info:
        return _render_code(token)
    path, width_px, height_px = info
    if not width_px or not height_px:
        return f'#fig-image("{path}")'
    # mermaid 用 24 px 字号出图；按 0.13 mm/px 缩放可让图内文字接近正文字号。
    # 再限制版心宽 145 mm、图高 185 mm，避免撑破页面或缩成针尖。
    width_mm = min(145.0, width_px * 0.13)
    height_mm = height_px * width_mm / width_px
    if height_mm > 185.0:
        return f'#fig-image("{path}", height: 185mm)'
    if width_mm < 143.0:
        return f'#fig-image("{path}", width: {width_mm:.0f}mm)'
    return f'#fig-image("{path}")'


def _render_block(tokens, i: int, depth: int, offset: int) -> tuple[int, str]:
    token = tokens[i]
    kind = token.type

    if kind == "heading_open":
        level = int(token.tag[1])
        if level == 2:
            match = _SECTION_RE.match(_plain_inline(tokens[i + 1]).strip())
            _CTX["section"] = match.group(1) if match else None
            _CTX["pseudo"] = 0
        return i + 3, "=" * (level + offset) + " " + _render_inline(tokens[i + 1])

    if kind == "paragraph_open":
        inline = tokens[i + 1]
        if _is_pseudo_heading(inline):
            # 以句号结尾的独立加粗段是正文里的强调句，不是小标题
            if _meaningful(inline.children)[1].content.rstrip().endswith("。"):
                return i + 3, _guard_line_start(_render_inline(inline))
            inner = _render_children(_meaningful(inline.children)[1:-1])
            if _CTX["section"]:
                _CTX["pseudo"] += 1
                number = f'{_CTX["section"]}.{_CTX["pseudo"]}'
                return i + 3, f'#pseudo-heading(number: "{number}")[' + inner + "]"
            return i + 3, "#pseudo-heading[" + inner + "]"
        if _is_caption(inline):
            inner = _render_children(_meaningful(inline.children)[1:-1])
            return i + 3, "#fig-caption[" + inner + "]"
        if CODE_CAPTION_RE.match(_plain_inline(inline).strip()):
            following = tokens[i + 3] if i + 3 < len(tokens) else None
            if following is not None and following.type in ("fence", "code_block"):
                info = (following.info or "").strip().split(" ")[0]
                if info != "mermaid":
                    return i + 4, _code_group(_render_code(following), following, _render_inline(inline))
            return i + 3, "#code-caption[" + _render_inline(inline) + "]"
        return i + 3, _guard_line_start(_render_inline(inline))

    if kind in ("bullet_list_open", "ordered_list_open"):
        return _render_list(tokens, i, depth, offset)

    if kind == "blockquote_open":
        return _render_blockquote(tokens, i, depth, offset)

    if kind == "table_open":
        return _render_table(tokens, i)

    if kind == "hr":
        return i + 1, "#v(1em)"

    if kind in ("html_block", "table_close", "blockquote_close", "list_item_close"):
        return i + 1, ""

    if kind in ("fence", "code_block"):
        if kind == "fence" and (token.info or "").strip().split(" ")[0] == "mermaid" and _RESOLVER:
            image = _render_mermaid(token)
            following = tokens[i + 1] if i + 1 < len(tokens) else None
            if (
                following is not None
                and following.type == "paragraph_open"
                and _is_caption(tokens[i + 2])
            ):
                inner = _render_children(_meaningful(tokens[i + 2].children)[1:-1])
                return i + 4, "#fig-group[\n" + image + "\n\n#fig-caption[" + inner + "]\n]"
            return i + 1, image
        return i + 1, _code_group(_render_code(token), token)

    return i + 1, ""


def convert(
    text: str,
    *,
    resolve_mermaid: Callable[[str], str] | None = None,
    heading_offset: int = 0,
) -> str:
    """把一段 Markdown 正文转成 Typst 标记（不含书籍骨架）。

    heading_offset 用于把 Markdown 的标题层级平移到书的层级：
    篇=1、章=2，故章内正文用 offset=1（H2→三级）。
    """
    global _RESOLVER, _CTX
    _RESOLVER = resolve_mermaid
    _CTX = {"section": None, "pseudo": 0}
    tokens = _md.parse(text)
    parts: list[str] = []
    i = 0
    while i < len(tokens):
        i, block = _render_block(tokens, i, 0, heading_offset)
        if block:
            parts.append(block)
    return "\n\n".join(parts).strip()
