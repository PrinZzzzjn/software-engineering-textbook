#!/usr/bin/env python3
"""检查节内小标题（**短语** 独占行）是否符合《节内小标题划分与命名规范 v2》。

只报告，不改文件。用法：
    python tools/check_subheads.py            # 全书
    python tools/check_subheads.py 09 16 22   # 指定章
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "软件工程实践-2.0"

# 标题体式：6–16 字（代码专名按词计），禁概括后缀词，禁句号结尾
BANNED = ("职责", "构成", "契约", "约束", "边界", "机制", "模型", "体系", "适用", "定位", "取舍", "维度", "原则")
MAX_PER_SECTION = 3
MAX_PER_SECTION_PARALLEL = 5


def display_len(text: str) -> int:
    # 代码专名与西文词各计 1 个单位，中文按字计
    text = re.sub(r"[A-Za-z0-9_.\-]+", "××", text)
    return len(text)


def scan(path: Path) -> tuple[list[str], list[tuple[str, int]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    problems: list[str] = []
    sections: list[tuple[str, int]] = []
    cur_sec = None
    count = 0

    def close():
        if cur_sec is not None:
            sections.append((cur_sec, count))

    for line in lines:
        m2 = re.match(r"^## (.+)$", line)
        if m2 and not line.startswith("###"):
            close()
            cur_sec, count = m2.group(1).strip(), 0
            continue
        m = re.match(r"^\*\*([^*]+)\*\*$", line)
        if not m or not cur_sec or not re.match(r"^\d+\.\d+", cur_sec):
            continue
        title = m.group(1).strip()
        if title.endswith(("。", "！", "？")):
            continue  # 句末加粗是正文强调句，转换脚本也不把它当标题
        count += 1
        if title.endswith(("。", "！", "？")):
            problems.append(f"[句号结尾] {cur_sec} · {title}")
        if display_len(title) < 4 or display_len(title) > 16:
            problems.append(f"[长度 {display_len(title)}] {cur_sec} · {title}")
        hit = [w for w in BANNED if w in title]
        if hit:
            problems.append(f"[禁用词 {','.join(hit)}] {cur_sec} · {title}")
        if title.startswith(("我", "你", "我们", "你们")):
            problems.append(f"[人称] {cur_sec} · {title}")
    close()

    for sec, n in sections:
        if n > MAX_PER_SECTION and n <= MAX_PER_SECTION_PARALLEL:
            problems.append(f"[数量 {n}] {sec}（并列结构可到 {MAX_PER_SECTION_PARALLEL}，请确认是否并列）")
        elif n > MAX_PER_SECTION_PARALLEL:
            problems.append(f"[数量 {n}] {sec} 超过上限 {MAX_PER_SECTION_PARALLEL}")
    return problems, sections


def main(argv: list[str]) -> int:
    files = sorted(ROOT.glob("0[1-9]-*.md")) + sorted(ROOT.glob("1[0-9]-*.md")) + sorted(ROOT.glob("2[0-4]-*.md"))
    if argv:
        wanted = set(argv)
        files = [f for f in files if f.name[:2] in wanted]

    total_problems = 0
    for path in files:
        problems, sections = scan(path)
        total = sum(n for _, n in sections)
        status = "OK" if not problems else f"{len(problems)} 项"
        print(f"{path.name:32s} 小标题 {total:2d} 条   {status}")
        for p in problems:
            print("    " + p)
        total_problems += len(problems)
    print(f"\n合计问题：{total_problems}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
