# -*- coding: utf-8 -*-
"""阶段 1：清除学生稿编写过程元数据，证据迁入作者向台账。

只做「删除行」，不改写任何正文行。规则：
1. `**验证**：✅/⚠️ …` 整行删除；
2. 紧随其后的 ```text 证据块（含 核验记录/运行命令/实际输出/结论/验证通过）连同围栏删除；
3. 其余仍含元数据的行不自动删除，打印 WARN 交人工判断。

用法：
  python tools/clean_metadata.py --dry-run
  python tools/clean_metadata.py --apply
"""
import argparse
import datetime
import pathlib
import re
import sys

from common import CODE_ICON_RE, DEFAULT_BOOK, META_RE, ROOT, student_files

LEDGER = ROOT / 'docs' / '作者校验台账_2.0.md'
EVIDENCE_KW = re.compile(r'核验记录|运行命令|实际输出|结论：|验证通过')
VALIDATION_LINE = re.compile(r'^\s*\*\*验证\*\*：')


def plan_file(p):
    """返回 (要删除的行号集合, 台账片段列表, 剩余命中行列表)"""
    lines = p.read_text(encoding='utf-8').splitlines(keepends=True)
    remove, ledger, leftover = set(), [], []
    i = 0
    while i < len(lines):
        if VALIDATION_LINE.match(lines[i]):
            start = i
            remove.add(i)
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                remove.add(j)
                j += 1
            if j < len(lines) and lines[j].strip().startswith('```'):
                k = j + 1
                body = []
                while k < len(lines) and not lines[k].strip().startswith('```'):
                    body.append(lines[k])
                    k += 1
                if k < len(lines) and EVIDENCE_KW.search(''.join(body)):
                    for x in range(j, k + 1):
                        remove.add(x)
                    m = k + 1
                    while m < len(lines) and lines[m].strip() == '':
                        remove.add(m)
                        m += 1
                    end = k
                else:
                    end = i
            else:
                end = i
            ledger.append((p.name, start + 1, end + 1, ''.join(lines[start:end + 1])))
            i = end + 1
            continue
        i += 1

    # 检查删除后是否仍有元数据命中（不含 00-教材设计.md 白名单）
    for idx, line in enumerate(lines):
        if idx not in remove and META_RE.search(CODE_ICON_RE.sub('', line)):
            leftover.append((idx + 1, line.rstrip()[:120]))
    return remove, ledger, leftover


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--path', default=None)
    args = ap.parse_args()
    if not (args.dry_run or args.apply):
        ap.error('必须指定 --dry-run 或 --apply')

    book = pathlib.Path(args.path).resolve() if args.path else DEFAULT_BOOK
    files = [p for p in student_files(book) if p.exists()]
    all_ledger, all_leftover, total_removed = [], [], 0
    for p in files:
        remove, ledger, leftover = plan_file(p)
        all_ledger += ledger
        all_leftover += [(p.name, *x) for x in leftover]
        total_removed += len(remove)
        if args.dry_run:
            print(f'{p.name}: 删除 {len(remove)} 行，验证片段 {len(ledger)} 个，残留命中 {len(leftover)}')
        if args.apply and remove:
            lines = p.read_text(encoding='utf-8').splitlines(keepends=True)
            p.write_text(''.join(l for i, l in enumerate(lines) if i not in remove), encoding='utf-8')

    print(f'合计：{len(files)} 个文件，删除 {total_removed} 行，验证片段 {len(all_ledger)} 个，残留命中 {len(all_leftover)}')
    for name, lineno, text in all_leftover[:15]:
        print(f'  WARN 残留 {name}:{lineno}: {text}')

    if args.apply:
        stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        out = [
            '# 作者校验台账（2.0）', '',
            f'> 迁出时间：{stamp}。来源：`软件工程实践-2.0/` 学生稿；本文件为**作者向**，不进教材、不付印。',
            f'> 共迁出 {len(all_ledger)} 个验证片段、{total_removed} 行。字段：来源文件 / 原行号范围 / 原文。', '',
        ]
        for name, start, end, text in all_ledger:
            out += [f'## `{name}` L{start}–L{end}', '', '```text', text.rstrip(), '```', '']
        LEDGER.write_text('\n'.join(out), encoding='utf-8')
        print(f'台账已写入 {LEDGER.relative_to(ROOT).as_posix()}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
