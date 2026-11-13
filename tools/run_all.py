# -*- coding: utf-8 -*-
"""汇总 10 个校验脚本，追加写入 docs/修订校验报告_2.0.md。

用法：
  python tools/run_all.py --scope book --stage 0 --expect-red
  python tools/run_all.py --scope book --stage 6 --require-green
"""
import argparse
import datetime
import json
import sys
from types import SimpleNamespace

from common import CHECKS, REPORT, resolve_book


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scope', default='book', choices=['book', 'all'])
    ap.add_argument('--path', default=None)
    ap.add_argument('--stage', default='0')
    ap.add_argument('--expect-red', action='store_true', help='阶段0：至少 6 个脚本应 RED')
    ap.add_argument('--require-green', action='store_true', help='全部脚本必须 GREEN')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    book = resolve_book(args.path)
    sub = SimpleNamespace(scope=args.scope, path=args.path, file=None, unit=None, json=False, stage=args.stage)
    results = []
    for name, fn in CHECKS:
        r = fn(book, sub)
        results.append((name, r))

    red = [n for n, r in results if not r['ok']]
    green = [n for n, r in results if r['ok']]
    stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    lines = [
        f'## stage {args.stage} · {stamp} · {"RED 基线" if args.expect_red else "校验"}',
        '',
        f'- 路径：`{book.relative_to(book.parent.parent).as_posix()}`',
        f'- 结果：**{len(green)} GREEN / {len(red)} RED**',
        '- 范围外已知未修：6 条断链、30 份教案错位（C8，不判失败）',
        '',
        '| 脚本 | 结果 | 关键指标 |',
        '| --- | --- | --- |',
    ]
    for name, r in results:
        metrics = '；'.join(f'{k}={v}' for k, v in r['metrics'].items() if k in (
            '命中数', '有效命中数', '合规章数', '节首信息条', '代码编号', '整段目标重复组', '单条目标重复组',
            '口径冲突', '缺失表述', '登记表', '悬空符号', '教材包内断链', '章号连续1-24',
            '章内习题数', '98答案题数', 'v3.0结构特征', '<details>', '二维码/挂载点',
            '独立习题标注数', '记忆+理解占比'))
        lines.append(f'| `{name}` | {"GREEN" if r["ok"] else "RED"} | {metrics} |')
    lines += ['', '### 未通过项摘要', '']
    for name, r in results:
        if not r['ok'] and r['issues']:
            lines.append(f'- **{name}**：' + '；'.join(r['issues'][:4]))
    lines += ['', '---', '']

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open('a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    if args.json:
        print(json.dumps({'stage': args.stage, 'green': green, 'red': red}, ensure_ascii=False, indent=2))
    else:
        print(f'stage {args.stage}: {len(green)} GREEN / {len(red)} RED  -> {REPORT.name}')
        for n in red:
            print(f'  RED  {n}')
        for n in green:
            print(f'  GREEN {n}')

    if args.expect_red and len(red) < 6:
        print('ERROR: --expect-red 要求至少 6 个脚本跑红，实际不足，脚本口径可能失效', file=sys.stderr)
        return 1
    if args.require_green and red:
        print('ERROR: --require-green 未满足', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
