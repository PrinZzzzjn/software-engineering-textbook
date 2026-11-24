#!/usr/bin/env python3
"""机械验收章节审查报告与正文哈希。"""

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = ROOT / "软件工程实践-2.0"
REPORTS = ROOT / "docs" / "章节审查"
BASELINE = REPORTS / "00-审查前SHA256.txt"

H2 = [
    "## 一、本章路线",
    "## 二、骨架审查",
    "## 三、三级标题对照",
    "## 四、行文审查",
    "## 五、优先级与下一步",
    "## 六、核对范围与未核事项",
]
ROUTE = [
    "1. 上一章止步于",
    "2. 本章接手",
    "3. 本章产出",
    "4. 下一章接手",
]
HEADING_HEADER = "| 位置 | 现有标题/粗体标签 | 处理 | 建议标题 | T1 | T2 | T3 | 依据 |"

SKELETON_FIELDS = [
    "- 位置：",
    "- 类型：",
    "- 原文证据：",
    "- 判定问题与结论：",
    "- 建议改法：",
    "- 优先级：",
]
PROSE_FIELDS = [
    "- 位置：",
    "- 类型：",
    "- 原文证据：",
    "- 终极判定问题与结论：",
    "- 建议改法：",
    "- 优先级：",
]


def baseline_digests():
    out = {}
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) >= 2:
            out[parts[0]] = parts[1]
    return out


def sections_of(text):
    positions = [(h, text.index(h)) for h in H2]
    out = {}
    for i, (h, start) in enumerate(positions):
        end = positions[i + 1][1] if i + 1 < len(positions) else len(text)
        out[h] = text[start:end]
    return out


def nonempty_field(block, field):
    for line in block.splitlines():
        if line.startswith(field):
            return bool(line[len(field) :].strip())
    return False


def check_findings(section, marker, fields, label):
    blocks = re.split(rf"^#### {re.escape(marker)}-", section, flags=re.M)[1:]
    if not blocks:
        return None if "未发现" in section else f"{label}问题清单为空且未写未发现"
    for i, block in enumerate(blocks, 1):
        body = re.split(r"^#### ", block, maxsplit=1, flags=re.M)[0]
        for field in fields:
            if not nonempty_field(body, field):
                return f"{label}-{i} 缺少或留空字段 {field}"
    return None


def check(n, digests):
    nn = f"{n:02d}"
    files = list(CHAPTERS.glob(f"{nn}-*.md"))
    if len(files) != 1:
        return f"{nn} FAIL: 章节文件不唯一: {files}"
    report = REPORTS / f"{nn}-章审查.md"
    if not report.exists():
        return f"{nn} FAIL: 报告不存在"
    text = report.read_text(encoding="utf-8")
    missing = [h for h in H2 if not re.search(rf"^{re.escape(h)}\s*$", text, re.M)]
    if missing:
        return f"{nn} FAIL: 缺少二级标题: {missing}"
    sections = sections_of(text)
    route = sections[H2[0]]
    missing = [
        r
        for r in ROUTE
        if not re.search(rf"^{re.escape(r)}：[^\s\n]", route, re.M)
    ]
    if missing:
        return f"{nn} FAIL: 路线字段缺失或为空: {missing}"
    heading = sections[H2[2]]
    if HEADING_HEADER not in heading:
        return f"{nn} FAIL: 三级标题对照表头缺失或不在对应章节"
    table_lines = [
        line
        for line in heading.splitlines()
        if line.startswith("|")
        and not line.startswith(HEADING_HEADER)
        and not re.match(r"^\|[\s:\-|]+\|$", line)
    ]
    if not table_lines:
        return f"{nn} FAIL: 三级标题对照表无数据行"
    if any(line.count("|") < 9 for line in table_lines):
        return f"{nn} FAIL: 三级标题对照表行列数不足"
    problem = check_findings(sections[H2[1]], "骨架", SKELETON_FIELDS, "骨架")
    if problem:
        return f"{nn} FAIL: {problem}"
    problem = check_findings(sections[H2[3]], "行文", PROSE_FIELDS, "行文")
    if problem:
        return f"{nn} FAIL: {problem}"
    actual = hashlib.sha256(files[0].read_bytes()).hexdigest()
    expected = digests.get(nn)
    if expected is None or actual != expected:
        return f"{nn} FAIL: 正文 SHA256 变化"
    return f"{nn} PASS"


def main():
    if len(sys.argv) < 2:
        print("usage: check_chapter_audit_reports.py <章号...>", file=sys.stderr)
        return 1
    digests = baseline_digests()
    results = []
    for arg in sys.argv[1:]:
        try:
            n = int(arg)
        except ValueError:
            results.append(f"{arg} FAIL: 章号非整数")
            continue
        results.append(check(n, digests))
    for line in results:
        print(line)
    return 0 if all(r.endswith(" PASS") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
