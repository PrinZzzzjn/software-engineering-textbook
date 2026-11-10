# -*- coding: utf-8 -*-
"""校验 1.x 基线快照完整性：python tools/verify_snapshot.py --snapshot docs/_基线快照_1.x"""
import argparse
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', default='docs/_基线快照_1.x')
    args = ap.parse_args()
    snap = (ROOT / args.snapshot).resolve()
    manifest = snap / 'CHECKSUMS.sha256'
    if not manifest.exists():
        print(f'FAIL: 缺清单 {manifest}')
        return 1
    bad = []
    n = 0
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        digest, rel = line.split('  ', 1)
        p = snap / rel
        if not p.exists():
            bad.append(f'缺文件 {rel}')
            continue
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != digest:
            bad.append(f'校验和不符 {rel}')
        n += 1
    print(f'{"OK" if not bad else "FAIL"}: 校验 {n} 个文件')
    for b in bad[:10]:
        print('  ' + b)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
