# -*- coding: utf-8 -*-
"""2.0 三段式迁移（2026-11-10 用户裁决）。

口径：取消引导练习层，四段式改三段（概念讲解 → 示范例题 → 独立习题）；
删去全部【Bloom：应用】独立习题（应用层由示范例题承担），保留其余
思考题与课后自习题；保留题重编为连续 N-1..N-k；答案统一在 98。

用法（在 C13 之前的教材状态下执行）：
    python tools/migrate_3stage.py            # dry-run，输出清单与引用改写预览
    python tools/migrate_3stage.py --apply    # 落盘（章节 + 98 答案）
    python tools/migrate_3stage.py --apply --only 03   # 样板章

注意：这是一次性迁移脚本。**C13 落盘后不可重复执行**（analyse 会因找不到
引导练习段而断言失败）；如需复跑，先用 git 把教材目录还原到 C13 之前的提交。
"""
import argparse
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / '软件工程实践-2.0'
ANS = BOOK / '98-参考答案.md'

SEC_GUIDED = re.compile(r'^## (?:\d+\.\d+ 引导练习|三、引导练习)\s*$')
SEC_INDEP = re.compile(r'^## (?:\d+\.\d+ 独立习题|五、独立习题)\s*$')
HEAD_INDEP = re.compile(r'^#### 习题 (\d+)-(\d+)([^\n]*)【Bloom：([^】]+)】')
HEAD_DEMO = re.compile(r'^#### 例 (\d+)-(\d+)[：:]')
HEAD_GUIDED = re.compile(r'^#### 例 (\d+)-(\d+)（引导练习）')
REF_EX = re.compile(r'例\s*(\d+)-(\d+)')
REF_INDEP = re.compile(r'习题\s*(\d+)-(\d+)')
REF_RANGE = re.compile(r'(\d+)-(\d+)\s*[～~]\s*(?:(\d+)-)?(\d+)')
REF_LIST = re.compile(
    r'习题\s*((\d+)-(\d+)((?:\s*(?:[、,，]|与|及|和)\s*(?:\d+-)?\d+)*))'
    r'(\s*第\s*[\d、]+\s*(?:项|小题|条))?'
)
LIST_SEG = re.compile(r'(?:[、,，]|与|及|和)\s*((?:(\d+)-)?(\d+))')


def chapters():
    out = []
    for p in sorted(BOOK.glob('*.md')):
        m = re.match(r'^(\d{2})-', p.name)
        if m and 1 <= int(m.group(1)) <= 26:
            out.append(p)
    return out


def load(p):
    return p.read_bytes().decode('utf-8').splitlines(keepends=True)


def save(p, lines):
    p.write_bytes(''.join(lines).encode('utf-8'))


def sections(lines):
    idx = [i for i, l in enumerate(lines) if l.startswith('## ')]
    return [(i, idx[k + 1] if k + 1 < len(idx) else len(lines), lines[i].rstrip('\r\n'))
            for k, i in enumerate(idx)]


def analyse(p):
    lines = load(p)
    n = int(p.name[:2])
    secs = sections(lines)
    guided_sec = next((s for s in secs if SEC_GUIDED.match(s[2])), None)
    indep_sec = next((s for s in secs if SEC_INDEP.match(s[2])), None)
    assert guided_sec, f'{p.name}: 找不到引导练习段'
    assert indep_sec, f'{p.name}: 找不到独立习题段'

    demo, guided_demo = [], []
    for l in lines:
        m = HEAD_DEMO.match(l.rstrip('\r\n'))
        if m:
            demo.append(m.group(2))
        m = HEAD_GUIDED.match(l.rstrip('\r\n'))
        if m:
            guided_demo.append(m.group(2))
    assert demo, f'{p.name}: 无示范例题'

    ai, aj, _ = indep_sec
    heads = [i for i in range(ai, aj) if lines[i].startswith('#### 习题 ')]
    items = []
    for k, i in enumerate(heads):
        j = heads[k + 1] if k + 1 < len(heads) else aj
        m = HEAD_INDEP.match(lines[i].rstrip('\r\n'))
        assert m, f'{p.name}: 题头格式异常 {lines[i]!r}'
        items.append({'old': m.group(2), 'tail': m.group(3), 'bloom': m.group(4),
                      'start': i, 'end': j})
    keep = [x for x in items if x['bloom'] != '应用']
    drop = [x for x in items if x['bloom'] == '应用']
    assert keep, f'{p.name}: 删完无保留题'

    mapping, fallback = {}, {}
    for k, x in enumerate(keep, 1):
        x['new'] = str(k)
        mapping[(n, x['old'])] = x['new']
    for x in drop:
        same = [k for k in keep if k['bloom'] == x['bloom']]
        pool = same or keep
        best = min(pool, key=lambda k: abs(int(k['old']) - int(x['old'])))
        fallback[(n, x['old'])] = best['new']

    return {'p': p, 'n': n, 'lines': lines, 'secs': secs,
            'guided_sec': guided_sec, 'indep_sec': indep_sec,
            'demo': demo, 'guided_demo': guided_demo,
            'items': items, 'keep': keep, 'drop': drop,
            'mapping': mapping, 'fallback': fallback}


def build_maps(infos):
    indep_map, fallback, ex_map = {}, {}, {}
    for a in infos:
        indep_map.update(a['mapping'])
        fallback.update(a['fallback'])
        for old in a['guided_demo']:
            ex_map[(a['n'], old)] = a['demo'][-1]
    return indep_map, fallback, ex_map


def new_num(n, old, indep_map, fallback):
    if (n, old) in indep_map:
        return indep_map[(n, old)], False
    if (n, old) in fallback:
        return fallback[(n, old)], True
    return None, False


def rewrite_line(line, indep_map, fallback, ex_map):
    """改写单行中的题号引用；返回 (新行, 是否改动)。"""
    if line.startswith('#### '):
        return line, False
    orig = line

    # 1. 例题回链：指向已删除的引导练习时，改指该章最后一道示范例题
    def ex_sub(m):
        n, old = int(m.group(1)), m.group(2)
        if (n, old) in ex_map:
            return f'例 {n}-{ex_map[(n, old)]}'
        return m.group(0)
    line = REF_EX.sub(ex_sub, line)

    # 2. 范围引用 "5-1～5-5"：两端都按映射收敛
    def range_sub(m):
        n, a, tail_n, b = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        na, _ = new_num(n, a, indep_map, fallback)
        nb, _ = new_num(int(tail_n or n), b, indep_map, fallback)
        if na and nb:
            return f'{n}-{na}～{n}-{nb}'
        return m.group(0)
    line = REF_RANGE.sub(range_sub, line)

    # 3. 习题列举（含 "习题 7-1、7-2"、"2-1、2-3 与 2-6" 共享章号写法）
    #    指向已删题时丢弃「第 N 项」后缀，指向保留题时原样保留。
    def list_sub(m):
        whole = m.group(0)
        n, first, rest = int(m.group(2)), m.group(3), m.group(4)
        suffix = m.group(5) or ''
        head, head_dropped = new_num(n, first, indep_map, fallback)
        if not head:
            return whole
        out = [f'习题 {n}-{head}']
        seen = {head}
        if rest:
            for seg in LIST_SEG.finditer(rest):
                seg_n, seg_old = seg.group(2), seg.group(3)
                sn = int(seg_n) if seg_n else n
                v, _ = new_num(sn, seg_old, indep_map, fallback)
                if v and v not in seen:
                    out.append(f'{sn}-{v}')
                    seen.add(v)
        return '、'.join(out) + ('' if head_dropped else suffix)
    line = REF_LIST.sub(list_sub, line)

    # 5. 裸题号补丁（"其中 5-5 同时覆盖…"）
    def bare_sub(m):
        n, old = int(m.group(1)), m.group(2)
        v, dropped = new_num(n, old, indep_map, fallback)
        if v:
            return f'{n}-{v}'
        return m.group(0)
    line = re.sub(r'(?<=中 )(\d+)-(\d+)\b', bare_sub, line)

    return line, line != orig


def transform(a, indep_map, fallback, ex_map):
    lines = a['lines'][:]
    n = a['n']
    gi, gj, _ = a['guided_sec']
    ai, aj, atitle = a['indep_sec']

    # 删除引导练习段与【应用】题块（倒序删，避免下标漂移）
    cuts = [(gi, gj)] + [(x['start'], x['end']) for x in a['drop']]
    for i, j in sorted(cuts, reverse=True):
        del lines[i:j]

    # 题头重编 + 三段式段标题
    text = ''.join(lines)
    for x in a['keep']:
        text = text.replace(f'#### 习题 {n}-{x["old"]}【',
                            f'#### 习题 {n}-{x["new"]}【', 1)
    if n == 15:
        for old, new in (('## 四、质量评价', '## 三、质量评价'),
                         ('## 五、独立习题', '## 四、独立习题'),
                         ('## 六、本章小结与自检', '## 五、本章小结与自检')):
            text = text.replace(old, new, 1)
    else:
        # 用精确串替换：文件为 CRLF/LF 混合，行尾 \r 会让正则的 $ 失配。
        old_title, new_title = f'## {n}.4 独立习题', f'## {n}.3 独立习题'
        assert text.count(old_title) == 1, f'{a["p"].name}: 独立习题段标题异常'
        text = text.replace(old_title, new_title, 1)

    # 引用改写（逐行，便于 dry-run 对照）
    out, changes = [], []
    for line in text.splitlines(keepends=True):
        nl, changed = rewrite_line(line, indep_map, fallback, ex_map)
        if changed:
            changes.append((line.rstrip('\r\n'), nl.rstrip('\r\n')))
        out.append(nl)
    return out, changes


def transform_answers(indep_map, apply=False):
    lines = load(ANS)
    # 抬头：引导练习已取消，只保留示范例题的说明
    text = ''.join(lines)
    old_head = '> 建议先独立完成习题再对照。示范例题与引导练习的完整解答在各章正文内。'
    new_head = '> 建议先独立完成习题再对照。示范例题的完整解答在各章正文内，随题目给出；本章独立习题的参考答案集中放在这里。'
    text = text.replace(old_head, new_head, 1)
    lines = text.splitlines(keepends=True)

    heads = [i for i, l in enumerate(lines) if l.startswith('#### 习题 ')]
    cuts, renames = [], []
    for k, i in enumerate(heads):
        j = heads[k + 1] if k + 1 < len(heads) else len(lines)
        m = re.match(r'^#### 习题 (\d+)-(\d+)', lines[i])
        key = (int(m.group(1)), m.group(2))
        if key not in indep_map:
            cuts.append((i, j))
        else:
            renames.append((lines[i], lines[i].replace(
                f'习题 {key[0]}-{key[1]}', f'习题 {key[0]}-{indep_map[key]}', 1)))
    for i, j in sorted(cuts, reverse=True):
        del lines[i:j]
    text = ''.join(lines)
    for old, new in renames:
        text = text.replace(old, new, 1)
    if apply:
        save(ANS, text.splitlines(keepends=True))
    return len(renames), len(cuts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--only', help='只处理指定两位章号（样板用）')
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')

    files = chapters()
    if args.only:
        files = [p for p in files if p.name.startswith(args.only + '-')]
        assert files, f'找不到章 {args.only}'
    infos = [analyse(p) for p in files]
    # 样板模式下仍需全书映射，避免跨章引用误判
    all_infos = [analyse(p) for p in chapters()] if args.only else infos
    indep_map, fallback, ex_map = build_maps(all_infos)

    total_keep = sum(len(a['keep']) for a in all_infos)
    total_drop = sum(len(a['drop']) for a in all_infos)
    total_guided = sum(len(a['guided_demo']) for a in all_infos)
    print(f'全书：保留独立习题 {total_keep} 道 / 删除【应用】习题 {total_drop} 道 / 删除引导练习 {total_guided} 道')
    print(f'减量：{total_keep + total_drop + total_guided} → {total_keep} 道练习题（示范例题不动）')

    all_changes = []
    for a in infos:
        n = a['n']
        kept = ', '.join(f'{x["old"]}→{n}-{x["new"]}【{x["bloom"]}】' for x in a['keep'])
        dropped = ', '.join(f'{n}-{x["old"]}' for x in a['drop'])
        print(f'\n--- {a["p"].name} | 保留 {len(a["keep"])} 道：{kept}')
        print(f'    删除应用题：{dropped or "(无)"} | 删除引导练习段：例 {n}-' + f'、例 {n}-'.join(a['guided_demo']))
        out, changes = transform(a, indep_map, fallback, ex_map)
        all_changes += [(a['p'].name, o, w) for o, w in changes]
        if args.apply:
            save(a['p'], out)
        for o, w in changes:
            print(f'    引用: {o.strip()[:110]}')
            print(f'       → {w.strip()[:110]}')

    keep_n, drop_n = transform_answers(indep_map, apply=args.apply and not args.only)
    print(f'\n98 答案：保留并重编 {keep_n} 条，删除 {drop_n} 条')
    print(f'引用改写共 {len(all_changes)} 行')
    print('模式：' + ('APPLY（已落盘）' if args.apply else 'DRY-RUN（未写文件）'))


if __name__ == '__main__':
    main()
