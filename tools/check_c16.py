# -*- coding: utf-8 -*-
"""C16 专项探针：第 4–6 章「FastAPI 基础框架单元」四条检查。

设计口径（见 docs/4-6章重构规格_v3.0_待审核.md 第八节）：
  - 独立于 tools/common.py 的 CHECKS，**不占 10 项门禁**，保持「10 GREEN」守恒；
  - 只报警不判死：默认退出码 0；--strict 时任一 FAIL 返回 1；
  - 先跑 RED 作改造基线，样板与铺开完成后跑 GREEN。

2026-11-11 用户确认采用方案 B：第 5 章保留 schemas.py / deps.py / main.py
三文件种子，第 6 章用归位表放进模块优先目录 app/modules/<模块>/；因此
C16-3 的旧路径期望（app/routers、app/schemas）保留为报警，不判死。

用法：
  python tools/check_c16.py                 # 全量报警模式，打印四条检查明细
  python tools/check_c16.py --stage sample --strict   # 样板阶段验收（只判第 5 章可达成项）
  python tools/check_c16.py --json         # 机器可读
  python tools/check_c16.py --strict       # 全量验收模式，FAIL 即非零退出
  python tools/check_c16.py --path <教材目录>
"""
import argparse
import json
import re
import sys

from common import DEFAULT_BOOK, chapters, read, student_files

BANNED_5 = ('◇ 选读', '补课卡', '跳过不影响后续', '不要求一次学完')
K_CARD_RE = re.compile(r'K-0\d')
BACKREF_RE = re.compile(r'(?:第\s*5\s*章|本章)\s*5\.1\.(\d+)')
OLD_SECTION_RE = re.compile(r'第\s*5\s*章\s*5\.[4-9]')
SECTION_RE = re.compile(r'^### 5\.1\.(\d+)', re.M)
EX_HEAD_RE = re.compile(r'^#### 习题 (\d+-\d+)', re.M)
FLAT_FILE_RE = re.compile(r'\*\*代码 [^*]*\*\*\s*·\s*`(schemas|deps)\.py`')

ANCHORS = (
    ('prefix="/api/v1"', '统一前缀'),
    ('APIRouter(prefix="/departments"', '模块路由前缀'),
    ('title="Duty API"', '应用 title'),
)


def _book(path):
    return __import__('pathlib').Path(path) if path else DEFAULT_BOOK


def check1_no_optional(book, sample_only=False):
    """第 5 章无选读口径；◇ 课堂活动块必须保留。"""
    p = next((q for q in chapters(book) if q.name.startswith('05-FastAPI')), None)
    if not p:
        return False, ['未找到第 5 章文件']
    t = read(p)
    hits = [w for w in BANNED_5 if w in t]
    issues = [f'残留「{w}」{t.count(w)} 处' for w in hits]
    if '◇ 课堂活动块' not in t:
        issues.append('误删「◇ 课堂活动块」体例标记')
    return not issues, issues or ['第 5 章已全章转正，课堂活动块保留']


def check2_no_dangling(book, sample_only=False):
    """全书无补课卡 / K-0x；第 5 章回链节号与实际 ### 号一致。

    --stage sample 时只扫第 5 章与 98（样板阶段可独立达成），
    全量时扫全书（04/07/08/09/10/12/15/00-* 的引用留到铺开阶段 P3/P4）。
    """
    issues = []
    ch5 = next((q for q in chapters(book) if q.name.startswith('05-FastAPI')), None)
    ans = book / '98-参考答案.md'
    targets = [p for p in (ch5, ans) if p and p.exists()] if sample_only else \
        [p for p in student_files(book) if p.exists()] + ([ans] if ans.exists() else [])
    for p in targets:
        t = read(p)
        n = len(K_CARD_RE.findall(t)) + t.count('补课卡')
        if n:
            issues.append(f'{p.name}: 补课卡 / K-0x 残留 {n} 处')
        m = OLD_SECTION_RE.findall(t)
        if m:
            issues.append(f'{p.name}: 1.x 节号残留 {len(m)} 处')
    secs = {int(x) for x in SECTION_RE.findall(read(ch5))} if ch5 else set()
    ceiling = max(secs) if secs else 0
    for p in targets:
        for num in BACKREF_RE.findall(read(p)):
            if int(num) > ceiling:
                issues.append(f'{p.name}: 回链 5.1.{num} 超出实际节号 (最大 5.1.{ceiling})')
    scope = '第 5 章 + 98' if sample_only else '全书'
    return not issues, issues or [f'{scope}无补课卡 / K-0x / 过期回链；第 5 章实际 {ceiling} 节']


def check3_zero_rework(book, sample_only=False):
    """第 5 章最小工程目录 ⊆ 7.1.1 目录树；三处锚点两章逐字一致。

    样板阶段只判第 5 章侧；「第 7 章从本章起统一使用」等跨章项属铺开阶段 P3。
    """
    issues = []
    p5 = next((q for q in chapters(book) if q.name.startswith('05-FastAPI')), None)
    p7 = next((q for q in chapters(book) if q.name.startswith('07-')), None)
    if not p5 or not p7:
        return False, ['未找到第 5 / 7 章文件']
    t5, t7 = read(p5), read(p7)
    for m in FLAT_FILE_RE.finditer(t5):
        issues.append(f'第 5 章仍用平铺文件 {m.group(1)}.py（应改为 app/ 分层路径）')
    for token, label in ANCHORS:
        if token not in t5:
            issues.append(f'第 5 章缺锚点 {label}: {token}')
        if not sample_only and token not in t7 and label != '应用 title':
            issues.append(f'[铺开] 第 7 章缺锚点 {label}: {token}')
    if 'title="duty 最小工程"' in t5:
        issues.append('第 5 章 title 仍为「duty 最小工程」，与 7.1.5 不一致')
    if not sample_only and '从本章起统一使用' in t7:
        issues.append('[铺开] 第 7 章仍有「从本章起统一使用」另起炉灶表述')
    for path in ('app/routers/departments.py', 'app/schemas/', 'app/core/database.py'):
        if path not in t5:
            issues.append(f'第 5 章最小工程缺 7.1.1 目录: {path}')
        if not sample_only and path not in t7 and path != 'app/schemas/':
            issues.append(f'[铺开] 第 7 章缺目录: {path}')
    scope = '第 5 章侧' if sample_only else '两章'
    return not issues, issues or [f'四份文件路径与三处锚点{scope}一致']


def check4_exercise_alignment(book, sample_only=False):
    """4–6 章独立习题题头与 98 答案逐字对齐。

    规格原定第 5 章 4 → 5 道并同步 98；2026-11-11 用户限定本轮只改第 5 章，
    新增第 5 道顺延到铺开阶段（P1），故 sample 只判题头对齐，full 才判 5 道。
    """
    issues = []
    ans = book / '98-参考答案.md'
    answer_heads = set(EX_HEAD_RE.findall(read(ans))) if ans.exists() else set()
    for p in chapters(book):
        if p.name[:2] not in ('04', '05', '06'):
            continue
        heads = EX_HEAD_RE.findall(read(p))
        missing = [h for h in heads if h not in answer_heads]
        if missing:
            issues.append(f'{p.name}: 98 缺答案 {",".join(missing)}')
        if not sample_only and p.name[:2] == '05' and len(heads) != 5:
            issues.append(f'[铺开] 第 5 章独立习题 {len(heads)} 道（应为 5 道）')
    return not issues, issues or ['4–6 章题头与 98 对齐']


CHECKS = (
    ('C16-1 第5章无选读口径', check1_no_optional),
    ('C16-2 全书无补课卡与过期回链', check2_no_dangling),
    ('C16-3 最小工程零返工', check3_zero_rework),
    ('C16-4 习题与98答案对齐', check4_exercise_alignment),
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--path', default=None)
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--strict', action='store_true')
    ap.add_argument('--stage', default='full', choices=['sample', 'full'],
                    help='sample：只判第 5 章样板可独立达成的项；full：铺开后的全量验收')
    args = ap.parse_args()
    book = _book(args.path)
    results = []
    for name, fn in CHECKS:
        ok, detail = fn(book, args.stage == 'sample')
        results.append({'check': name, 'ok': ok, 'detail': detail})
    passed = sum(1 for r in results if r['ok'])
    if args.json:
        print(json.dumps({'stage': args.stage, 'passed': passed, 'total': len(results),
                          'results': results}, ensure_ascii=False, indent=2))
    else:
        print(f'C16 探针 [{args.stage}]：{passed} PASS / {len(results) - passed} FAIL  ({book.name})')
        for r in results:
            print(f'  {"PASS" if r["ok"] else "FAIL"}  {r["check"]}')
            for d in r['detail'][:8]:
                print(f'         - {d}')
            if len(r['detail']) > 8:
                print(f'         - …另有 {len(r["detail"]) - 8} 条')
    if args.strict and passed != len(results):
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
