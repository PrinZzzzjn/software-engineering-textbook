# -*- coding: utf-8 -*-
"""v3.0 一次性结构迁移脚本（C21 / C22）——**禁止重跑**。

只做机械部分：删旧 03、原 6–26 章改名 04–24、按来源文件重映射章号／节号／
题号／代码号／图表号。合并章 `03-后端开发框架.md` 已是新编号正文，由人工编写，
本脚本不生成、不改写它；98／前言／术语表另行人工迁移。

算法要点（v3.0 第八节）：
  - **按文件分别处理**，不做跨文件全局替换；
  - 章号引用支持范围与并列（第 8–14 章、第 5 章 5.3、5.4、5.5）；
  - 先保护「第 X 章 X.k」与「本章 X.k」，再处理本章自指，避免 6.x → 4.x
    之后再被 4.x → 3.x 二次命中；
  - 旧 4/5 章节号映射到新 3.1–3.6，旧 3 章节号统一落到第 2 章。

用法：
  python tools/migrate_v3.py --check      # 只做前置断言与影响面统计
  python tools/migrate_v3.py --apply      # 执行迁移（仅一次）
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / '软件工程实践-2.0'

CH_MAP = {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, **{i: i - 2 for i in range(6, 27)}}
SEC_MAP = {
    4: {1: '3.1', 2: '3.2', 3: '3.2', 4: '3.3'},
    5: {1: '3.4', 2: '3.4', 3: '3.5', 4: '3.6', 5: '3.5', 6: '3.6'},
}
SEP = r'[–\-—~、和与至]'
NUM_RUN = rf'\d+(?:\.\d+)?(?:\s*{SEP}\s*\d+(?:\.\d+)?)*'
EXT_SEC_RE = re.compile(rf'第\s*(\d+)\s*章\s*({NUM_RUN})')
OWN_SEC_RE = re.compile(rf'本章\s*({NUM_RUN})')
CH_RE = re.compile(rf'第\s*(\d+(?:\s*{SEP}\s*\d+)*)\s*章')
OBJ_RE = re.compile(r'(代码|表|图|例|习题|实训)\s*(\d+)-')


def _map_chapter(s):
    n = int(s)
    return str(CH_MAP.get(n, n))


def _map_section(ch, sec):
    ch, k = int(ch), int(str(sec).split('.')[-1])
    if ch in SEC_MAP:
        return SEC_MAP[ch].get(k, f'3.{k}')
    if ch == 3:
        return None  # 旧需求文档章节已删，由调用方落到「第 2 章」
    n = CH_MAP.get(ch, ch)
    return f'{n}.{k}'


def _rewrite_run(run, mapper):
    parts = re.split(rf'(\s*{SEP}\s*)', run)
    nums = [p.strip() for p in parts if p.strip() and not re.fullmatch(rf'\s*{SEP}\s*', p)]
    seps = [p for p in parts if re.fullmatch(rf'\s*{SEP}\s*', p)]
    mapped = [m for m in (mapper(x) for x in nums) if m is not None]
    out = []
    for m in mapped:
        if m not in out:
            out.append(m)
    if not out:
        return ''
    if len(out) == 1:
        return out[0]
    if any(re.search(r'[–\-—~至]', s) for s in seps):
        ordered = sorted(out, key=lambda x: tuple(int(p) for p in x.split('.')))
        return f'{ordered[0]}–{ordered[-1]}'
    return '、'.join(out)


def rewrite(text, old_n):
    """对单个章节文件（旧章号 old_n）做全部重映射。"""
    new_n = old_n - 2
    placeholders = {}

    def stash(s):
        key = f'\x00{len(placeholders)}\x00'
        placeholders[key] = s
        return key

    # 1) 「第 X 章 X.k…」：章号与节号一起映射
    def ext(m):
        ch, run = int(m.group(1)), m.group(2)
        if ch == 3:
            return stash('第 2 章')
        def f(sec):
            return _map_section(ch, sec)
        body = _rewrite_run(run, f)
        return stash(f'第 {_map_chapter(ch)} 章 {body}' if body else f'第 {_map_chapter(ch)} 章')
    text = EXT_SEC_RE.sub(ext, text)

    # 2) 「本章 X.k…」：按本章旧号映射到新号（节序号不变）
    def own(m):
        body = _rewrite_run(m.group(1), lambda sec: f'{new_n}.{int(str(sec).split(".")[-1])}')
        return stash(f'本章 {body}')
    text = OWN_SEC_RE.sub(own, text)

    # 3) 本章自指的裸节号 N.k → 新号（含 ## N.k 标题）；先占位，防止再被 4/5 规则二次命中
    text = re.sub(rf'(?<![\d.]){old_n}\.(\d+)',
                  lambda m: stash(f'{new_n}.{m.group(1)}'), text)

    # 3.5) 裸引旧 4/5 章节号（如「4.3 与 4.2」「、5.5（HTTPException）」）→ 新 3.x
    BARE_45_RE = re.compile(rf'(?<![\d.])((?:[45]\.\d+)(?:\s*{SEP}\s*[45]\.\d+)*)')
    text = BARE_45_RE.sub(
        lambda m: stash(_rewrite_run(m.group(1), lambda s: _map_section(s.split('.')[0], s))),
        text)

    # 4) 「第 X 章」及范围／并列
    def chref(m):
        body = _rewrite_run(m.group(1), _map_chapter)
        return stash(f'第 {body} 章')
    text = CH_RE.sub(chref, text)

    # 5) 题号／代码号／图表号／实训号前缀
    text = OBJ_RE.sub(lambda m: f'{m.group(1)} {CH_MAP.get(int(m.group(2)), int(m.group(2)))}-', text)

    for key, val in placeholders.items():
        text = text.replace(key, val)
    return text


def preflight():
    errors = []
    chaps = {int(p.name[:2]): p for p in BOOK.glob('*.md') if re.match(r'^\d{2}-', p.name)}
    for n in range(1, 27):
        if n not in chaps:
            errors.append(f'缺章文件: {n:02d}')
    if not (BOOK / '03-后端开发框架.md').exists():
        errors.append('缺新合并章 03-后端开发框架.md（应已由人工写就）')
    if (BOOK / '04-软件设计与建模.md').exists():
        errors.append('04-软件设计与建模.md 已存在，疑似已迁移，禁止重跑')
    for name in ('03-需求文档编写.md', '04-HTTP与接口设计.md', '05-FastAPI核心机制.md'):
        if not (BOOK / name).exists():
            errors.append(f'缺迁移前文件: {name}')
    return errors, chaps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    errors, chaps = preflight()
    if errors:
        print('PREFLIGHT FAILED:')
        for e in errors:
            print('  -', e)
        return 1
    if args.check or not args.apply:
        print('PREFLIGHT OK：26 章齐备，合并章已就位，旧 03/04/05 待删。')
        total = 0
        for n in range(6, 27):
            t = chaps[n].read_text(encoding='utf-8')
            changed = rewrite(t, n)
            if changed != t:
                total += 1
                print(f'  {chaps[n].name} → {n-2:02d}-…：将改写')
        print(f'预计改写 {total} 个章节文件；用 --apply 执行。')
        return 0

    # 1) 删旧 03/04/05
    for name in ('03-需求文档编写.md', '04-HTTP与接口设计.md', '05-FastAPI核心机制.md'):
        (BOOK / name).unlink()
        print(f'删除 {name}')
    # 2) 6–26 → 4–24（高号先行，避免目标名冲突）
    for n in range(26, 5, -1):
        src = chaps[n]
        dst = src.with_name(f'{n-2:02d}-' + src.name[3:])
        src.rename(dst)
        print(f'改名 {src.name} → {dst.name}')
    # 3) 引用重映射
    for n in range(6, 27):
        p = next(BOOK.glob(f'{n-2:02d}-*.md'))
        t = p.read_text(encoding='utf-8')
        new = rewrite(t, n)
        if new != t:
            p.write_text(new, encoding='utf-8')
            print(f'重映射 {p.name}')
    print('MIGRATION DONE。下一步：人工迁移 98／前言／术语表，再跑 check_migration.py。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
