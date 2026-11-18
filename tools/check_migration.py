# -*- coding: utf-8 -*-
"""v3.0 结构迁移五条断言（C21 / C22）。

对应 `docs/第3章与课次3裁撤及后端框架合并方案_v3.0_已签字.md` 第八节：
迁移前应 RED，迁移完成后应 GREEN。本脚本**不占 10 项门禁**，只作阶段 1–2
的先写 RED／后改 GREEN 判据，避免「边改结构边补内容」时口径漂移。

五条断言：
  A1 章号 1–24 连续，且 03 为新合并章；
  A2 章内题头与 98 答案题头全文逐字一致；
  A3 全书无「第 3 章 需求文档」类悬空引用，旧 03 章文件已删；
  A4 03/04 边界正确：03 讲 3.1–3.6、承载课次 3（含 ◆ 实训 3-1）；04 讲 4.1–4.6、承载课次 4 并含综合实训 4-1；
  A5 课次 3–5 的对照总表行与前言一致。

用法：
  python tools/check_migration.py            # 全部断言，任一 RED 退出码 1
  python tools/check_migration.py --json     # 机器可读
"""
import argparse
import json
import re
import sys
import pathlib

from common import DEFAULT_BOOK, read

CH_RE = re.compile(r'^(\d{2})-(.+)\.md$')
EX_HEAD_RE = re.compile(r'^#### 习题 (\d+-\d+)(.*)$', re.M)


def _chapters(book):
    out = {}
    for p in book.glob('*.md'):
        m = CH_RE.match(p.name)
        if m and 1 <= int(m.group(1)) <= 24:
            out[int(m.group(1))] = p
    return out


def a1_numbering(chaps):
    nums = sorted(chaps)
    issues = []
    missing = [n for n in range(1, 25) if n not in chaps]
    extra = [n for n in nums if n > 24]
    if missing:
        issues.append('缺章号: ' + ','.join(map(str, missing)))
    if extra:
        issues.append('超出 24 的章号: ' + ','.join(map(str, extra)))
    third = chaps.get(3)
    if third is None or '后端开发框架' not in third.name:
        issues.append('第 3 章不是《后端开发框架》合并章')
    return {
        'ok': not issues,
        'metrics': {'章数': len(chaps), '章号': f'{nums[0] if nums else "-"}–{nums[-1] if nums else "-"}',
                    '第3章文件': third.name if third else '缺失'},
        'issues': issues,
    }


def a2_heads(book, chaps):
    heads = {}
    bad_prefix = []
    for n, p in chaps.items():
        for m in EX_HEAD_RE.finditer(read(p)):
            if int(m.group(1).split('-')[0]) != n:
                bad_prefix.append(f'{p.name}: 习题 {m.group(1)}')
            heads[m.group(1)] = m.group(0).strip()
    ans = book / '98-参考答案.md'
    ans_heads = {}
    if ans.exists():
        for m in EX_HEAD_RE.finditer(read(ans)):
            ans_heads[m.group(1)] = m.group(0).strip()
    only_book = sorted(set(heads) - set(ans_heads))
    only_ans = sorted(set(ans_heads) - set(heads))
    diff = [f'{k}: 章内「{heads[k]}」/ 98「{ans_heads[k]}」'
            for k in sorted(set(heads) & set(ans_heads)) if heads[k] != ans_heads[k]]
    issues = bad_prefix + [f'98 缺答案 {k}' for k in only_book] + [f'章内缺题目 {k}' for k in only_ans] + diff
    return {
        'ok': not issues,
        'metrics': {'章内题头': len(heads), '98题头': len(ans_heads),
                    '题号前缀错位': len(bad_prefix), '题头不一致': len(diff)},
        'issues': issues,
    }


def a3_no_reqdoc(book, chaps):
    issues = []
    old = book / '03-需求文档编写.md'
    if old.exists():
        issues.append('旧文件仍在: 03-需求文档编写.md')
    for p in book.glob('*.md'):
        t = read(p)
        for pat, label in (
            (r'第\s*3\s*章[^\n]{0,4}需求文档', '「第 3 章 需求文档」'),
            (r'^#{1,2}\s*第\s*3\s*章\s*需求文档编写', '「第 3 章 需求文档编写」标题'),
        ):
            for m in re.finditer(pat, t, re.M):
                line_no = t[:m.start()].count('\n') + 1
                issues.append(f'{p.name}:{line_no} {label}')
    return {
        'ok': not issues,
        'metrics': {'旧03文件': old.exists(), '悬空引用': len(issues)},
        'issues': issues[:20],
    }


def a4_boundary(chaps):
    p3 = chaps.get(3)
    p4 = chaps.get(4)
    issues = []
    if p3 is None or '后端开发框架' not in p3.name:
        issues.append('第 3 章不是《后端开发框架》')
    if p4 is None or '软件设计与建模' not in p4.name:
        issues.append('第 4 章不是《软件设计与建模》')
    t3 = read(p3) if p3 else ''
    t4 = read(p4) if p4 else ''
    nums3 = [f'{a}.{b}' for a, b in re.findall(r'^## (\d+)\.(\d+) ', t3, re.M)]
    nums4 = [f'{a}.{b}' for a, b in re.findall(r'^## (\d+)\.(\d+) ', t4, re.M)]
    if nums3 != [f'3.{i}' for i in range(1, 7)]:
        issues.append(f'第 3 章讲解小节应为 3.1–3.6，实际 {nums3}')
    if nums4 != [f'4.{i}' for i in range(1, 7)]:
        issues.append(f'第 4 章讲解小节应为 4.1–4.6，实际 {nums4}')
    if '◆ 实训 3-1' not in t3:
        issues.append('第 3 章缺 ◆ 实训 3-1')
    if '◆ 综合实训 4-1' not in t4:
        issues.append('第 4 章缺 ◆ 综合实训 4-1')
    old = re.findall(r'^## [56]\.\d+ ', t4, re.M)
    if old:
        issues.append('第 4 章残留旧 5.k / 6.k 节号: ' + '；'.join(old[:5]))
    return {
        'ok': not issues,
        'metrics': {'03小节': '/'.join(nums3), '04小节': '/'.join(nums4),
                    '04实训': '◆ 综合实训 4-1' in t4},
        'issues': issues,
    }


def a5_lesson_map(book, chaps):
    fore = book / '00-前言.md'
    ft = read(fore) if fore.exists() else ''
    p3 = chaps.get(3)
    p4 = chaps.get(4)
    t3 = read(p3) if p3 else ''
    t4 = read(p4) if p4 else ''
    issues = []
    row3 = next((l for l in ft.splitlines() if l.startswith('| 3 |')), '')
    row4 = next((l for l in ft.splitlines() if l.startswith('| 4 |')), '')
    row5 = next((l for l in ft.splitlines() if l.startswith('| 5 |')), '')
    checks = [
        (row3, '第 3 章', '4（2 理论 + 2 实践）', 'T + P', '课次 3'),
        (row4, '第 4 章', '4（2 理论 + 2 实践）', 'T + P', '课次 4'),
        (row5, '第 5 章', '4 实践', 'P', '课次 5'),
    ]
    for row, ch, hours, typ, label in checks:
        if ch not in row:
            issues.append(f'对照总表{label}行未指向{ch}: {row[:80]}')
        if hours not in row:
            issues.append(f'对照总表{label}行不是 {hours}')
        if f'| {typ} |' not in row:
            issues.append(f'对照总表{label}行类型不是 {typ}')
    return {
        'ok': not issues,
        'metrics': {'课次3行': row3[:40] or '缺失', '课次4行': row4[:40] or '缺失',
                    '课次5行': row5[:40] or '缺失'},
        'issues': issues,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--path', default=None)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    book = pathlib.Path(args.path).resolve() if args.path else DEFAULT_BOOK
    chaps = _chapters(book)
    results = [
        ('A1 章号1-24连续', a1_numbering(chaps)),
        ('A2 题头全文一致', a2_heads(book, chaps)),
        ('A3 无需求文档章', a3_no_reqdoc(book, chaps)),
        ('A4 03/04边界正确', a4_boundary(chaps)),
        ('A5 课次3-5对照一致', a5_lesson_map(book, chaps)),
    ]
    red = [n for n, r in results if not r['ok']]
    if args.json:
        print(json.dumps({'ok': not red, 'red': red,
                          'results': {n: r for n, r in results}}, ensure_ascii=False, indent=2))
    else:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        for name, r in results:
            print(f'[{"GREEN" if r["ok"] else "RED"}] {name}')
            for k, v in r['metrics'].items():
                print(f'  {k}: {v}')
            for line in r['issues'][:8]:
                print(f'  - {line}')
        print(f'{"ALL GREEN" if not red else "RED: " + ", ".join(red)}')
    return 0 if not red else 1


if __name__ == '__main__':
    sys.exit(main())
