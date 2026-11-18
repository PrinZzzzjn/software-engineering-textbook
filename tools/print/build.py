"""教材样书构建入口：Markdown → Typst → PDF。"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from md2typst import convert
from mermaid_render import collect_blocks, hash_block, image_size, render_all

REPO_ROOT = Path(__file__).resolve().parents[2]
PRINT_DIR = Path(__file__).resolve().parent
TYPST = REPO_ROOT / "build" / "pdf-toolchain" / "bin" / "typst-x86_64-pc-windows-msvc" / "typst.exe"
SOURCE_DIR = REPO_ROOT / "软件工程实践-2.0"
OUTPUT_DIR = REPO_ROOT / "样书"
WORK_DIR = REPO_ROOT / "build" / "print"
MERMAID_DIR = REPO_ROOT / "build" / "mermaid"

FRONT = [
    ("00-前言.md", "前言"),
    ("00-概念地图.md", "全书概念地图"),
]

APPENDICES = [
    ("术语表.md", "附录 A", "术语表"),
    ("98-参考答案.md", "附录 B", "参考答案（教师用）"),
    ("99-表现性任务.md", "附录 C", "表现性任务"),
]

_CHAPTER_RE = re.compile(r"^#\s*第\s*(\d+)\s*章\s*(.+?)\s*$")
_PART_RE = re.compile(r"^###\s*(第[一二三四五六七八九十]+篇)\s*(.+?)\s*$")
_ITEM_RE = re.compile(r"^- 第\s*(\d+)\s*章")

EDITORIAL_MARKERS = ("编排位置", "本版为教材内容修订版")


def compile_typ(typ_path: Path, out_pdf: Path) -> None:
    """编译单个 .typ，根目录固定为仓库根，便于用 /build/mermaid 这类绝对路径引图。"""
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [str(TYPST), "compile", "--root", str(REPO_ROOT), str(typ_path), str(out_pdf)],
        check=True,
        cwd=REPO_ROOT,
    )


def chapter_files() -> list[Path]:
    files = sorted(SOURCE_DIR.glob("0[1-9]-*.md")) + sorted(SOURCE_DIR.glob("1[0-9]-*.md"))
    files += sorted(SOURCE_DIR.glob("2[0-4]-*.md"))
    return files


def chapter_meta(path: Path) -> tuple[str, str]:
    first = path.read_text(encoding="utf-8").splitlines()[0]
    match = _CHAPTER_RE.match(first)
    if not match:
        raise ValueError(f"章标题不合格式：{path.name}: {first}")
    return f"第 {match.group(1)} 章", match.group(2)


def _strip_body(text: str) -> str:
    """去掉文件首行的 H1，只留正文（H1 由书籍骨架生成）。"""
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    return "\n".join(lines)


def _drop_editorial(text: str) -> str:
    """去掉写给编者自己看的引用块，与前言里那节手写目录。"""
    kept: list[str] = []
    skip_section = False
    skip_quote = False
    for line in text.splitlines():
        if skip_quote:
            if line.startswith(">"):
                continue
            skip_quote = False
        if line.startswith("## 目录"):
            skip_section = True
            continue
        if skip_section and line.startswith("## "):
            skip_section = False
        if skip_section:
            continue
        if line.startswith(">") and any(marker in line for marker in EDITORIAL_MARKERS):
            skip_quote = True
            continue
        kept.append(line)
    return "\n".join(kept)


def parts_from_preface() -> list[tuple[str, str, int]]:
    """从 00-前言 的手写目录里取出四篇的名称与起始章。"""
    text = (SOURCE_DIR / "00-前言.md").read_text(encoding="utf-8")
    parts: list[tuple[str, str, int]] = []
    current: str | None = None
    current_title = ""
    for line in text.splitlines():
        part = _PART_RE.match(line)
        if part:
            current, current_title = part.group(1), part.group(2)
            continue
        item = _ITEM_RE.match(line)
        if item and current and not any(p[0] == current for p in parts):
            parts.append((current, current_title, int(item.group(1))))
    return parts


def _resolver(text: str):
    blocks = collect_blocks(text)
    if not blocks:
        return None
    rendered = render_all(blocks, MERMAID_DIR)

    def resolve(block: str):
        path = rendered.get(hash_block(block))
        if path is None:
            return None
        width, height = image_size(path)
        return ("/" + path.relative_to(REPO_ROOT).as_posix(), width, height)

    return resolve


def _body_typst(path: Path, *, drop_editorial: bool = False) -> str:
    text = path.read_text(encoding="utf-8")
    if drop_editorial:
        text = _drop_editorial(text)
    text = _strip_body(text)
    return convert(text, heading_offset=1, resolve_mermaid=_resolver(text))


def cover() -> str:
    return """#page(header: none, footer: none, numbering: none)[
  #v(1fr)
  #align(center)[
    #text(font: fonts.head, size: 36pt, weight: "bold")[软件工程实践]
    #linebreak()
    #v(2mm)
    #text(font: fonts.head, size: 24pt)[第 2 版]
    #v(16mm)
    #text(font: fonts.head, size: 16pt)[#meta.subtitle]
    #v(44mm)
    #text(size: 12pt)[#meta.date]
  ]
  #v(1fr)
]"""


def book_typst() -> str:
    chunks: list[str] = ['#import "/tools/print/style.typ": *', "#show: template", cover()]

    for name, label in FRONT:
        path = SOURCE_DIR / name
        chunks.append(f'#section("{label}")')
        chunks.append(_body_typst(path, drop_editorial=True))

    chunks.append("#toc-page()")
    chunks.append('#pagebreak(to: "odd", weak: true)\n#counter(page).update(1)\n#set page(numbering: "1")')

    parts = {start: (no, title) for no, title, start in parts_from_preface()}
    seen_parts: set[str] = set()
    for path in chapter_files():
        no, title = chapter_meta(path)
        number = int(no.replace("第", "").replace("章", "").strip())
        if number in parts and parts[number][0] not in seen_parts:
            part_no, part_title = parts[number]
            seen_parts.add(part_no)
            chunks.append(f'#part("{part_no}", "{part_title}")')
        chunks.append(f'#chapter("{no}", "{title}")')
        chunks.append(_body_typst(path))

    for name, no, title in APPENDICES:
        chunks.append(f'#section("{no} {title}")')
        chunks.append(_body_typst(SOURCE_DIR / name, drop_editorial=True))

    return "\n\n".join(chunks)


def build_book(out_pdf: Path) -> Path:
    typ = WORK_DIR / "book.typ"
    typ.parent.mkdir(parents=True, exist_ok=True)
    typ.write_text(book_typst(), encoding="utf-8")
    compile_typ(typ, out_pdf)
    return out_pdf


def build_chapters(out_dir: Path) -> list[Path]:
    written: list[Path] = []
    out_dir.mkdir(parents=True, exist_ok=True)
    # 清掉上一轮的分章 PDF（改名后旧文件会残留）
    for stale in out_dir.glob("*.pdf"):
        stale.unlink()
    for path in chapter_files():
        no, title = chapter_meta(path)
        typ = WORK_DIR / "chapters" / f"{path.stem}.typ"
        typ.parent.mkdir(parents=True, exist_ok=True)
        typ.write_text(
            '#import "/tools/print/style.typ": *\n#show: template\n#set page(numbering: "1")\n'
            f'#chapter("{no}", "{title}")\n\n' + _body_typst(path),
            encoding="utf-8",
        )
        number, _, name = path.stem.partition("-")
        out = out_dir / f"第{number}章-{name}.pdf"
        compile_typ(typ, out)
        written.append(out)
    return written


def build_preview(typ: Path, out_dir: Path, pages: str = "1-8") -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("page-*.png"):
        stale.unlink()
    subprocess.run(
        [
            str(TYPST),
            "compile",
            "--root",
            str(REPO_ROOT),
            "--format",
            "png",
            "--ppi",
            "110",
            "--pages",
            pages,
            str(typ),
            str(out_dir / "page-{0p}.png"),
        ],
        check=True,
        cwd=REPO_ROOT,
    )
    return sorted(out_dir.glob("page-*.png"))


def page_count(pdf: Path) -> int:
    try:
        from pypdf import PdfReader
    except ImportError:  # pragma: no cover
        return 0
    return len(PdfReader(str(pdf)).pages)


def write_notes(out_dir: Path, book_pdf: Path | None, chapters: list[Path], previews: list[Path]) -> Path:
    lines = [
        "# 排版说明",
        "",
        "本目录由 `tools/print/build.py` 生成，源码与正文改动后重跑即可。",
        "",
        "## 版式参数",
        "",
        "| 项目 | 取值 |",
        "| --- | --- |",
        "| 开本 | A4 210×297 mm |",
        "| 页边距 | 上 25 / 下 25 / 订口 30 / 切口 22 mm（双面镜像） |",
        "| 正文字体 | 宋体 SimSun 10.5 pt，行距 1.6 |",
        "| 标题字体 | 黑体 SimHei（章 22 pt、节 15 pt、三级 12 pt、四级 10.5 pt） |",
        "| 代码 | Consolas 8.5 pt，浅灰底，超出版心的长行在词边界自动换行 |",
        "| 页码 | 卷首罗马数字，正文阿拉伯数字从 1 起 |",
        "| 表 | 三线表，表内 9 pt |",
        "| 图 | mermaid 转矢量 SVG，题注 9 pt 居中 |",
        "",
        "## 重新生成",
        "",
        "```bash",
        "python tools/print/build.py --all --out 样书/",
        "```",
        "",
        "改版式只动 `tools/print/style.typ` 顶部的参数区；改 Markdown 转换规则动 `tools/print/md2typst.py`。",
        "",
        "## 本次产出",
        "",
    ]
    if book_pdf:
        lines.append(f"- 合订本：`{book_pdf.name}`，{page_count(book_pdf)} 页")
    lines.append(f"- 分章 PDF：{len(chapters)} 份")
    lines.append(f"- 预览图：{len(previews)} 张")
    path = out_dir / "排版说明.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成教材送审样书 PDF")
    parser.add_argument("--book", action="store_true", help="生成合订本")
    parser.add_argument("--chapters", action="store_true", help="生成分章 PDF")
    parser.add_argument("--all", action="store_true", help="合订本 + 分章 + 预览")
    parser.add_argument("--out", default=str(OUTPUT_DIR), help="输出目录")
    args = parser.parse_args(argv)

    if not (args.book or args.chapters or args.all):
        args.all = True

    out_arg = Path(args.out)
    if out_arg.suffix.lower() == ".pdf":
        book_target = out_arg
        out_root = out_arg.parent
    else:
        out_root = out_arg
        book_target = out_root / "软件工程实践-2.0-送审样书.pdf"
    out_root.mkdir(parents=True, exist_ok=True)

    book_pdf = None
    chapters: list[Path] = []
    previews: list[Path] = []

    if args.book or args.all:
        book_pdf = build_book(book_target)
        print(f"合订本：{book_pdf}（{page_count(book_pdf)} 页）")

    if args.chapters or args.all:
        chapters = build_chapters(out_root / "分章")
        print(f"分章：{len(chapters)} 份 → {out_root / '分章'}")

    if args.all:
        previews = build_preview(WORK_DIR / "book.typ", out_root / "预览")
        print(f"预览：{len(previews)} 张 → {out_root / '预览'}")

    notes = write_notes(out_root, book_pdf, chapters, previews)
    print(f"说明：{notes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
