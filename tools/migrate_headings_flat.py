# -*- coding: utf-8 -*-
"""一次性迁移：章节标题扁平化（2026-11-12 用户裁决，不可重跑）。

口径：
1. 删除每章 `## N.1 概念讲解` 标题行及其后紧邻的一个空行；
2. 原 `### N.1.k 标题` 提为二级标题并简化编号 -> `## N.k 标题`；
3. `## N.2 示范例题` -> `## 示范例题`，`## N.3 独立习题` -> `## 独立习题`；
4. 教材目录内所有 `N.1.k` 形式的回链引用 -> `N.k`（章内、跨章、98 答案、
   前言、教材设计），节号前缀从三位收敛为两位；
5. 结果：一章内只有原概念讲解下的小节带序号，其余二级标题均为无编号纯文字，
   与「本章小结」一致。示范例题 / 独立习题下的 `####` 条目保持四级不动。

防重跑：以「每章必须存在且仅存在一个 ## N.1 概念讲解」为前置断言。
行尾：逐行处理、原样保留 CRLF / LF，不统一换行符。
回滚：从 git 提交或改动前备份恢复（本脚本不负责回滚）。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / '软件工程实践-2.0'

# N 限定 1-26，k 限定 1-2 位；前后不得紧邻数字或点，避免误伤版本号 / IP / 库版本。
REF = re.compile(r'(?<![\d.])([1-9]|1[0-9]|2[0-6])\.1\.(\d{1,2})(?![\d.])')
SEC_CONCEPT = re.compile(r'^## (\d{1,2})\.1 概念讲解[ \t]*$')
SEC_SUB = re.compile(r'^### (\d{1,2})\.1\.(\d{1,2})([ \t]+.*)$')
SEC_DEMO = re.compile(r'^## \d{1,2}\.2 示范例题[ \t]*$')
SEC_INDEP = re.compile(r'^## \d{1,2}\.3 独立习题[ \t]*$')


def chapters():
    return sorted(p for p in BOOK.glob('[0-9][0-9]-*.md')
                  if re.match(r'^(0[1-9]|1[0-9]|2[0-6])-', p.name))


def load(p):
    with p.open('r', encoding='utf-8', newline='') as f:
        return f.read().splitlines(keepends=True)


def save(p, lines):
    with p.open('w', encoding='utf-8', newline='') as f:
        f.write(''.join(lines))


def eol(line):
    if line.endswith('\r\n'):
        return '\r\n'
    if line.endswith('\n'):
        return '\n'
    return ''


def bare(line):
    return line.rstrip('\r\n')


def migrate_chapter(p):
    lines = load(p)
    n = int(p.name[:2])
    out, skip_blank = [], False
    cnt = {'concept': 0, 'sub': 0, 'demo': 0, 'indep': 0, 'ref': 0}
    for line in lines:
        raw = bare(line)
        if skip_blank:
            skip_blank = False
            if raw.strip() == '':
                continue
        m = SEC_CONCEPT.match(raw)
        if m:
            assert int(m.group(1)) == n, f'{p.name}: 概念讲解章号异常 {raw}'
            cnt['concept'] += 1
            skip_blank = True
            continue
        m = SEC_SUB.match(raw)
        if m:
            assert int(m.group(1)) == n, f'{p.name}: 小节章号异常 {raw}'
            out.append(f'## {n}.{m.group(2)}{m.group(3)}' + eol(line))
            cnt['sub'] += 1
            continue
        if SEC_DEMO.match(raw):
            out.append('## 示范例题' + eol(line))
            cnt['demo'] += 1
            continue
        if SEC_INDEP.match(raw):
            out.append('## 独立习题' + eol(line))
            cnt['indep'] += 1
            continue
        new_raw, k = REF.subn(lambda mm: f'{mm.group(1)}.{mm.group(2)}', raw)
        cnt['ref'] += k
        out.append(new_raw + eol(line))
    assert cnt['concept'] == 1, f'{p.name}: 概念讲解段 {cnt["concept"]} 个（应为 1），脚本可能已重跑'
    assert cnt['demo'] == 1, f'{p.name}: 示范例题段 {cnt["demo"]} 个（应为 1）'
    assert cnt['indep'] == 1, f'{p.name}: 独立习题段 {cnt["indep"]} 个（应为 1）'
    assert cnt['sub'] >= 3, f'{p.name}: 提级小节仅 {cnt["sub"]} 个'
    save(p, out)
    return cnt


def migrate_refs_only(p):
    lines = load(p)
    out, total = [], 0
    for line in lines:
        raw = bare(line)
        new_raw, k = REF.subn(lambda mm: f'{mm.group(1)}.{mm.group(2)}', raw)
        total += k
        out.append(new_raw + eol(line))
    if total:
        save(p, out)
    return total


def main():
    chs = chapters()
    assert len(chs) == 26, f'章节数 {len(chs)}，应为 26'
    # 前置断言：全书仍为旧结构，防止重跑
    bad = [p.name for p in chs if not any(SEC_CONCEPT.match(bare(l)) for l in load(p))]
    assert not bad, f'以下章缺 ## N.1 概念讲解，脚本不可重跑: {bad}'

    totals = {'concept': 0, 'sub': 0, 'demo': 0, 'indep': 0, 'ref': 0}
    for p in chs:
        c = migrate_chapter(p)
        for k in totals:
            totals[k] += c[k]
        print(f'{p.name}: 删概念讲解 1 / 提级 {c["sub"]} 节 / 去编号 2 段 / 回链 {c["ref"]} 处')

    others = [p for p in sorted(BOOK.glob('*.md')) if p not in chs]
    for p in others:
        k = migrate_refs_only(p)
        if k:
            totals['ref'] += k
            print(f'{p.name}: 回链重映射 {k} 处')

    print('---')
    print(f'全书：删除概念讲解壳 {totals["concept"]} 个 / 提级小节 {totals["sub"]} 个 / '
          f'去编号段 {totals["demo"] + totals["indep"]} 个 / 编号引用重映射 {totals["ref"]} 处')
    return 0


if __name__ == '__main__':
    sys.exit(main())
