#!/usr/bin/env python3
"""扫描各章「本章要解决的问题」，报告违反去具体化判据的表述。

判据见 docs/superpowers/specs/2026-11-18-章首件去具体化-design.md 的 D2、D3。
只检查章首件一节，不判人工项（D6 需通读）。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "软件工程实践-2.0"
HEADING = "## 本章要解决的问题"
RULES = [
    (re.compile(r"```"), "代码块"),
    (re.compile(r"`[^`\n]+`"), "行内代码"),
    (re.compile(r"→"), "箭头"),
    (re.compile(r"(?<![\w.])[1-5]\d{2}(?![\w.])"), "状态码"),
    (re.compile(r"/api/|127\.0\.0\.1|localhost"), "地址"),
    (re.compile(r"[0-9二两三四五六七八九十]+\s*(条|类|项|步|件|种)"), "数量+量词"),
    (
        re.compile(
            r"[0-9二两三四五六七八九十]+\s*个(文件|模块|问题|步骤|坑|页面|部分|"
            r"方面|阶段|层次|环节|动作|角色|组件|工具|命令|指标|概念|案例)"
        ),
        "数量+量词",
    ),
    (re.compile(r"[一二两三四五六七八九十]+\s*分钟"), "时长"),
    (re.compile(r"[（(][A-Za-z][A-Za-z /-]{1,30}[）)]"), "英文括注"),
]


def section_lines(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == HEADING), None)
    if start is None:
        return []
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    return [(i + 1, lines[i]) for i in range(start, end)]


def main():
    problems = 0
    for path in sorted(ROOT.glob("[0-2][0-9]-*.md")):
        entries = section_lines(path)
        body = [
            (idx, item)
            for idx, item in enumerate(entries)
            if item[1].strip() and not item[1].startswith("## ")
        ]
        last_idx = body[-1][0] if body else None
        question_skipped = False
        for idx, (lineno, line) in enumerate(entries):
            if line.startswith("## "):
                continue
            if not question_skipped and line.strip():
                question_skipped = True
                if line.strip().startswith("**") and line.strip().endswith("？**"):
                    continue
            for pattern, label in RULES:
                # 数量与时长只在本节最后一段（路径段）判，现象段的自然计数不算。
                if label in ("数量+量词", "时长") and idx != last_idx:
                    continue
                if pattern.search(line):
                    problems += 1
                    print(f"{path.name}:{lineno}  {label}  {line.strip()[:60]}")
    print(f"\n共 {problems} 处")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
