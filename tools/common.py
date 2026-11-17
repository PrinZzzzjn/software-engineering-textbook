# -*- coding: utf-8 -*-
"""《软件工程实践》教材 2.0 修订校验脚本共用模块。

约定：
- 默认扫描 `软件工程实践-2.0/`（工作副本），可用 --path 切换。
- --scope book 只扫教材内容包；--scope all 额外扫描 docs/ 与 教学设计/ 的已知断链（仅登记）。
- 学生稿 = 24 章 + 98-参考答案.md；`00-教材设计.md` 为作者向白名单，其 M0x 素材索引合法。
"""
import argparse
import collections
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_BOOK = ROOT / '软件工程实践-2.0'
MAIN_BOOK = ROOT / '软件工程实践'
SNAPSHOT = ROOT / 'docs' / '_基线快照_1.x'
REPORT = ROOT / 'docs' / '修订校验报告_2.0.md'

CHAPTER_RE = re.compile(r'^(0[1-9]|1\d|2[0-4])-.*\.md$')
META_RE = re.compile(r'已验证|核验记录|M0[1-9]|实际输出|运行命令|⚠️|✅')
# 合法代码图标（第 20 章 st.toast(message, icon="✅")），不是编写过程元数据
CODE_ICON_RE = re.compile(r'icon="✅"')
WHITELIST = {'00-教材设计.md'}
BLOOM_LEVELS = ('记忆', '理解', '应用', '分析', '评价', '创造')


def read(p):
    return p.read_text(encoding='utf-8')


def chapters(book):
    return sorted(p for p in book.glob('*.md') if CHAPTER_RE.match(p.name))


def student_files(book):
    return chapters(book) + [book / '98-参考答案.md']


def resolve_book(arg=None):
    return pathlib.Path(arg).resolve() if arg else DEFAULT_BOOK


def _res(ok, metrics, issues=None):
    return {'ok': bool(ok), 'metrics': metrics, 'issues': issues or []}


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scope', default='book', choices=['book', 'all'])
    ap.add_argument('--path', default=None, help='教材包目录，默认 软件工程实践-2.0/')
    ap.add_argument('--file', default=None, help='只检查指定文件名')
    ap.add_argument('--unit', default=None, help='课次单元联合校验，如 lesson4')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--stage', default='-')
    return ap.parse_args()


def main(name, fn):
    # Windows 控制台默认 GBK，打印 ✅ 等字符会抛 UnicodeEncodeError；统一按 UTF-8 输出。
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    args = parse_args()
    book = resolve_book(args.path)
    r = fn(book, args)
    if args.json:
        print(json.dumps({'check': name, **r}, ensure_ascii=False, indent=2))
    else:
        flag = 'GREEN' if r['ok'] else 'RED'
        print(f'[{flag}] {name}')
        for k, v in r['metrics'].items():
            print(f'  {k}: {v}')
        for line in r['issues'][:12]:
            print(f'  - {line}')
        if len(r['issues']) > 12:
            print(f'  ... 另有 {len(r["issues"]) - 12} 条')
    sys.exit(0 if r['ok'] else 1)


# ---------------------------------------------------------------- 检查项

def check_metadata(book, args):
    files = [p for p in student_files(book) if p.exists() and p.name not in WHITELIST]
    if args.file:
        files = [p for p in files if p.name == args.file]
    raw, effective, by_file = 0, 0, {}
    for p in files:
        text = read(p)
        raw += len(META_RE.findall(text))
        n_eff = sum(len(META_RE.findall(CODE_ICON_RE.sub('', line))) for line in text.splitlines())
        if n_eff:
            by_file[p.name] = n_eff
        effective += n_eff
    return _res(effective == 0, {
        '命中数': raw,
        '有效命中数': effective,
        '代码图标白名单': 'icon="✅" 不计',
        '文件数': len(files),
        '白名单': ', '.join(sorted(WHITELIST)),
        '命中分布(前5)': dict(list(by_file.items())[:5]),
    }, [f'{k}: {v} 处' for k, v in by_file.items()])


def _fenced_blocks(t):
    """列出全部围栏块 (lang, body)，用于区分 mermaid 图与真正代码块。"""
    lines = t.splitlines()
    blocks, i = [], 0
    fence = re.compile(r'^```([A-Za-z0-9]*)\s*$')
    while i < len(lines):
        m = fence.match(lines[i])
        if not m:
            i += 1
            continue
        lang = m.group(1) or 'plain'
        j, body = i + 1, []
        while j < len(lines) and not lines[j].startswith('```'):
            body.append(lines[j]); j += 1
        blocks.append((lang, '\n'.join(body)))
        i = j + 1
    return blocks


def _code_caption_ok(t):
    """G-01 判据：任何围栏块内都不得混入代码编号；无代码块的章豁免编号。

    2026-11-10 扩展：原判据只查 mermaid，漏掉了 rollout_style 把「闭合围栏」
    误判为开围栏后插进普通代码块内部的 `**代码 X-Y-Z** · 示例（文本）`
    （全书 19 章 148 处）。这类标签会印在代码里、破坏 Python 语法。
    """
    blocks = _fenced_blocks(t)
    for _, body in blocks:
        if '**代码 ' in body:
            return False
    if any(lang != 'mermaid' for lang, _ in blocks):
        return bool(re.search(r'代码 \d+-\d+-\d+', t))
    return True


def _structure_one(p):
    t = read(p)
    # C19：章内带序号的二级标题只能是讲解小节，且须为 N.1、N.2… 连续编号。
    # 既防旧三位节号回归，也防第 15 章「质量评价」这类非讲解块与讲解小节撞号。
    n = int(p.name[:2])
    secs = [f'{a}.{b}' for a, b in re.findall(r'^## (\d+)\.(\d+) ', t, re.M)]
    need = {
        '节首信息条': '对应课次' in t,
        '学习目标': bool(re.search(r'^## 本章学习目标', t, re.M)),
        '代码编号': _code_caption_ok(t),
        # 2026-11-10 口径变更：换场景总表 / 章末评价 / 本章提示页 / AI 侧栏
        # 四类章末部件全部取消，判据反向，防止体例脚本重跑时回归。
        '无换场景总表': not re.search(r'^## 换场景总表', t, re.M),
        '无章末评价': not re.search(r'^## 章末(评价要点|质量评价量表)', t, re.M),
        '无本章提示页': not re.search(r'^## 本章提示页', t, re.M),
        '无AI侧栏': not re.search(r'^## AI 侧栏', t, re.M) and 'AI 了解性侧栏' not in t,
        # 2026-11-10 C13：四段式改三段，引导练习段全部取消；判据防体例脚本重跑回归。
        '无引导练习段': not re.search(r'^## .*引导练习', t, re.M),
        '有独立习题段': bool(re.search(r'^## .*独立习题', t, re.M)),
        # 2026-11-12 C19：概念讲解外壳取消；讲解小节提为带序号二级标题（N.k），
        # 示范例题 / 独立习题改为无编号二级标题，与「本章小结」同级。
        # 一章内只有讲解小节带序号；防体例脚本重跑把旧结构注回来。
        '无概念讲解段': not re.search(r'^## .*概念讲解', t, re.M),
        '有编号讲解小节': bool(secs),
        '讲解小节编号连续': secs == [f'{n}.{i}' for i in range(1, len(secs) + 1)],
        '示范例题无编号': bool(re.search(r'^## 示范例题[ \t]*\r?$', t, re.M)),
        '独立习题无编号': bool(re.search(r'^## 独立习题[ \t]*\r?$', t, re.M)),
        '无三位节号标题': not re.search(r'^### \d+\.\d+\.\d+ ', t, re.M),
        '无带号段标题': not re.search(r'^## \d+\.[23] (示范例题|独立习题)[ \t]*\r?$', t, re.M),
    }
    return need


def check_structure(book, args):
    files = chapters(book)
    if args.file:
        files = [p for p in files if p.name == args.file]
    per, missing = {}, []
    for p in files:
        need = _structure_one(p)
        per[p.name] = need
        lack = [k for k, v in need.items() if not v]
        if lack:
            missing.append(f'{p.name}: 缺 {"/".join(lack)}')
    ok_chapters = sum(1 for v in per.values() if all(v.values()))
    info = sum(1 for v in per.values() if v['节首信息条'])
    code = sum(1 for v in per.values() if v['代码编号'])

    # C21（2026-11-12）：第 4、5 章并入新第 3 章，「课次 4 单元」四处补偿全部作废，
    # 本检查不再要求两章节首「本单元第 1/2 章」，也不再检查前言分组行。
    return _res(ok_chapters == len(files), {
        '合规章数': f'{ok_chapters}/{len(files)}',
        '节首信息条': f'{info}/{len(files)}',
        '代码编号': f'{code}/{len(files)}',
    }, missing)


def _goal_text(t):
    m = re.search(r'^## 本章学习目标\s*\n(.*?)(?=^## |\Z)', t, re.M | re.S)
    return m.group(1) if m else ''


def _norm(s):
    return re.sub(r'\s+', '', s)


def check_goals(book, args):
    files = chapters(book)
    if args.file:
        files = [p for p in files if p.name == args.file]
    whole = collections.defaultdict(list)
    items = collections.defaultdict(set)
    counts = {}
    for p in files:
        body = _goal_text(read(p))
        whole[_norm(body)].append(p.name[:2])
        items_of = [re.sub(r'^\s*\d+\.\s*', '', l).strip() for l in body.splitlines() if l.strip()]
        counts[p.name[:2]] = len([x for x in items_of if not x.startswith('读完')])
        for line in items_of:
            if len(line) > 8:
                items[_norm(line)].add(p.name[:2])
    rep_whole = {k: v for k, v in whole.items() if k and len(v) > 1}
    rep_items = {k: v for k, v in items.items() if len(v) > 1}
    too_few = [c for c, n in counts.items() if n < 4]
    return _res(not rep_whole and not rep_items and not too_few, {
        '整段目标重复组': len(rep_whole),
        '整段重复涉及章数': sum(len(v) for v in rep_whole.values()),
        '单条目标重复组': len(rep_items),
        '单条重复涉及章数': len(set().union(*rep_items.values())) if rep_items else 0,
        '目标不足4条的章': len(too_few),
    }, [f'整段重复: {"/".join(v)}' for v in rep_whole.values()]
       + [f'目标仅 {counts[c]} 条: 第{c}章' for c in too_few])


def check_consistency(book, args):
    fore, design = book / '00-前言.md', book / '00-教材设计.md'
    ft, dt = (read(fore) if fore.exists() else ''), (read(design) if design.exists() else '')
    ledger = ROOT / 'docs' / '修订裁决记录_2.0.md'
    conflicts, required = [], []
    if '章号与课程课次一一对应' in ft:
        conflicts.append('前言仍写「章号与课程课次一一对应」')
    m01_rows = [l for l in dt.splitlines() if l.startswith('| M01 |')]
    if any('结构基准' in l for l in m01_rows):
        conflicts.append('素材索引 M01 行仍标注「结构基准」')
    for label, text, needle in (
        ('前言·模拟数据声明', ft, '教学模拟数据'),
        ('前言·课次3分组行', ft, '课次 3 · 后端开发框架'),
        ('前言·课次3学时', ft, '课次 3 · 后端开发框架（2 学时理论 ＋ 2 学时实践）'),
        ('前言·课次4–5分组行', ft, '课次 4–5 · 软件设计与建模'),
        ('前言·第13章实训块', ft, '含一个实训块'),
        ('前言·对照总表', ft, '章 ↔ 课次'),
        ('前言·第3章新名', ft, '后端开发框架'),
        ('前言·第4章新名', ft, '软件设计与建模'),
        ('教材设计·T/P 两套子体例', dt, 'T/P 两套子体例'),
        ('裁决记录', read(ledger) if ledger.exists() else '', 'C12'),
    ):
        if needle not in text:
            required.append(label)
    return _res(not conflicts and not required, {
        '口径冲突': len(conflicts),
        '缺失表述': len(required),
        '裁决记录存在': ledger.exists(),
    }, ['冲突: ' + c for c in conflicts] + ['缺: ' + r for r in required])


def check_concepts(book, args):
    reg = ROOT / 'docs' / '概念首次出现登记表_2.0.md'
    if not reg.exists():
        return _res(False, {'登记表': '不存在', '核销': '0/9'}, ['登记表未建立'])
    t = read(reg)
    # 只统计「一、9 组概念登记」里的数据行（以 | C- 开头）；原实现靠 K- 或数字单元格猜行，
    # 会漏掉无补课卡的条目（JWT、SECRET_KEY），导致行数永远到不了 9。
    rows = [l for l in t.splitlines() if l.startswith('| C-')]
    unchecked = [l for l in rows if '未核销' in l or l.rstrip().endswith('|  |')]
    return _res(not unchecked and len(rows) >= 9, {'登记表': '存在', '行数': len(rows), '未核销': len(unchecked)},
                [f'未核销: {l[:60]}' for l in unchecked])


def check_code(book, args):
    # 关键符号须有定义或明确回链；1.x 的 07/08 章有悬空符号。
    # 判据按「全书」而非「单章」：符号在任一章有定义，或在第 5 章集中讲解过，
    # 都不算悬空——第 8 章之后的业务章本就通过 import / Depends 复用，不应要求章章重写定义。
    targets = {'create_access_token', 'APIRouter', 'include_router', 'get_db'}
    texts = {p.name: read(p) for p in chapters(book)}

    def defined_in(t, sym):
        return bool(re.search(r'(def|class|=)\s*' + re.escape(sym), t))

    defined_global = {sym: any(defined_in(t, sym) for t in texts.values()) for sym in targets}
    concept_chapter = next((t for n, t in texts.items() if '后端开发框架' in n), '')
    for sym in targets:
        if sym in concept_chapter:
            defined_global[sym] = True

    issues = []
    for name, t in texts.items():
        for sym in targets:
            if sym not in t:
                continue
            linked = bool(re.search(r'(见第\s*\d+\s*章|完整工程见|代码文件清单|回链)', t))
            if not defined_in(t, sym) and not linked and not defined_global[sym]:
                issues.append(f'{name}: {sym} 既无定义也无回链')
    mini = book / '03-后端开发框架.md'
    if not mini.exists():
        issues.append('第 3 章最小工程章不存在')
    return _res(not issues, {'悬空符号': len(issues), '最小工程章': mini.exists()}, issues)


def relative_links(p, text):
    for m in re.finditer(r'\[[^\]]*\]\(([^)]+)\)', text):
        u = m.group(1).split('#')[0].strip()
        if not u or u.startswith(('http', 'https', 'mailto')):
            continue
        yield u


def check_links(book, args):
    bad = []
    for p in book.glob('*.md'):
        for u in relative_links(p, read(p)):
            if not (p.parent / u).resolve().exists():
                bad.append(f'{p.name} -> {u}')
    outside = []
    if args.scope == 'all':
        for p in list((ROOT / 'docs').glob('*.md')) + list((ROOT / '教学设计').rglob('*.md')):
            for u in relative_links(p, read(p)):
                if not (p.parent / u).resolve().exists():
                    outside.append(f'{p.relative_to(ROOT).as_posix()} -> {u}')
    return _res(not bad, {
        '教材包内断链': len(bad),
        '范围外断链(登记)': len(outside) if args.scope == 'all' else '不扫描',
    }, bad + [f'[范围外·已知未修] {x}' for x in outside])


def check_numbering(book, args):
    chaps = chapters(book)
    nums = sorted(int(p.name[:2]) for p in chaps)
    continuous = nums == list(range(1, 25))
    bad_prefix = []
    head_re = re.compile(r'^#### 习题 (\d+-\d+)(.*)$', re.M)
    book_heads = {}
    for p in chaps:
        n = int(p.name[:2])
        for m in head_re.finditer(read(p)):
            if int(m.group(1).split('-')[0]) != n:
                bad_prefix.append(f'{p.name}: 习题 {m.group(1)}')
            book_heads[m.group(1)] = m.group(0).strip()
    ans = book / '98-参考答案.md'
    answer_heads = {}
    if ans.exists():
        for m in head_re.finditer(read(ans)):
            answer_heads[m.group(1)] = m.group(0).strip()
    only_book = sorted(set(book_heads) - set(answer_heads))
    only_ans = sorted(set(answer_heads) - set(book_heads))
    head_diff = [
        f'{k}: 章内「{book_heads[k]}」/ 98「{answer_heads[k]}」'
        for k in sorted(set(book_heads) & set(answer_heads))
        if book_heads[k] != answer_heads[k]
    ]
    missing = [f'98 缺答案 {k}' for k in only_book] + [f'章内缺题目 {k}' for k in only_ans]
    # v3.0 结构特征（C21）：原 03 删除、原 04/05 并入新 03、原 06–26 → 新 04–24
    structural = {
        '合并章': (book / '03-后端开发框架.md').exists(),
        '第4章新名': (book / '04-软件设计与建模.md').exists(),
        '末章': (book / '24-软件部署综合实践.md').exists(),
        '旧03/04/05已删': not any((book / n).exists() for n in (
            '03-需求文档编写.md', '04-HTTP与接口设计.md', '05-FastAPI核心机制.md')),
    }
    struct_bad = [k for k, v in structural.items() if not v]
    issues = bad_prefix + missing + head_diff + [f'v3.0结构未实施: {s}' for s in struct_bad]
    return _res(continuous and not issues, {
        '章号连续1-24': continuous,
        '章内习题数': len(book_heads),
        '98答案题数': len(answer_heads),
        '题号前缀错位': len(bad_prefix),
        '题头全文不一致': len(head_diff),
        'v3.0结构特征': 'OK' if not struct_bad else ','.join(struct_bad),
    }, issues)


def check_paper(book, args):
    # 00-教材设计.md 是作者向文件，其中「无二维码 / 无折叠交互」是规则说明，不是挂载点
    all_md = [p for p in book.glob('*.md') if p.name not in WHITELIST]
    details = sum(read(p).count('<details') for p in all_md)
    # 「扫码」是需求举例中的普通词（第 2 章），不是资源挂载点，故不纳入
    qr = sum(len(re.findall(r'二维码|数字资源挂载点|在线资源包', read(p))) for p in all_md)
    fold = sum(len(re.findall(r'点击展开|展开查看|折叠', read(p))) for p in all_md)
    return _res(details == 0 and qr == 0 and fold == 0, {
        '<details>': details, '二维码/挂载点': qr, '展开折叠措辞': fold,
    }, [f'<details> 仍有 {details} 处', f'二维码措辞 {qr} 处', f'折叠措辞 {fold} 处'] if (details or qr or fold) else [])


def check_bloom(book, args):
    heads = collections.Counter()
    for p in student_files(book):
        if not p.exists():
            continue
        for m in re.finditer(r'^#### 习题 \d+-\d+【Bloom：([^】]+)】', read(p), re.M):
            heads[m.group(1).strip()] += 1
    total = sum(heads.values())
    low = heads['记忆'] + heads['理解']
    ratio = round(low / total * 100, 1) if total else 0
    theory_concept = 0
    per_chapter = {}
    for p in chapters(book):
        t = read(p)
        if re.search(r'概念辨析|原理解释|为什么需要', t):
            theory_concept += 1
        per_chapter[p.name[:2]] = len(re.findall(r'^#### 习题 \d+-\d+', t, re.M))
    too_few = [n for n, c in per_chapter.items() if c < 2]
    # C13（2026-11-10）：三段式 + 删【应用】题后，章内与 98 各印一份。
    # C21（2026-11-12）：26 章 → 24 章，阈值按「24 章 × 每章至少 2 道 × 两份」= 96 设定。
    errs = []
    if theory_concept < 6:
        errs.append(f'理论章概念题不足: {theory_concept}/6')
    if total < 96:
        errs.append(f'独立习题标注数不足: {total}/96')
    if too_few:
        errs.append(f'每章少于 2 道独立习题: {",".join(too_few)}')
    return _res(theory_concept >= 6 and total >= 96 and not too_few, {
        '独立习题标注数': total,
        '记忆+理解': low,
        '记忆+理解占比': f'{ratio}%',
        '分布': dict(heads),
        '含概念辨析章数': theory_concept,
        '每章最少习题数': min(per_chapter.values()) if per_chapter else 0,
    }, errs)


CHECKS = [
    ('metadata', check_metadata),
    ('structure', check_structure),
    ('goals', check_goals),
    ('consistency', check_consistency),
    ('concepts', check_concepts),
    ('code', check_code),
    ('links', check_links),
    ('numbering', check_numbering),
    ('paper', check_paper),
    ('bloom', check_bloom),
]
