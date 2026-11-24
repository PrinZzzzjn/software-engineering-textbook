# -*- coding: utf-8 -*-
"""执勤电子年鉴案例数据事实源工具。

用法：
  python tools/case_data.py show
  python tools/case_data.py set baseline departments D001 address 一号营区
  python tools/case_data.py build
  python tools/case_data.py check
  python tools/case_data.py diff
  python tools/case_data.py apply --yes
"""
from __future__ import annotations

import argparse
import datetime as _datetime
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT / "data" / "case_data.yaml"
DEFAULT_OUTPUT = ROOT / "data" / "case_data.json"
EXCLUDED_PARTS = {
    ".git", "venv", ".venv", "__pycache__", "build", "node_modules",
    ".pytest_cache", "offline-deps", ".superpowers",
    # 本地工作树副本与本地记忆不属于课程活跃内容；B 档快照保留历史取值供对照。
    ".claude", ".workbuddy", "snapshot-b",
}
SCAN_SUFFIXES = {".py", ".md", ".txt", ".json"}


def _json_default(value):
    if isinstance(value, (_datetime.date, _datetime.datetime)):
        return value.isoformat(sep=" ") if isinstance(value, _datetime.datetime) else value.isoformat()
    return str(value)


def load_source(path: Path | None = None) -> dict:
    src = Path(path) if path else DEFAULT_SOURCE
    return yaml.safe_load(src.read_text(encoding="utf-8"))


def save_source(doc: dict, path: Path | None = None) -> None:
    dst = Path(path) if path else DEFAULT_SOURCE
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")


def set_field(doc: dict, dataset: str, entity: str, record_id: str, field: str, value) -> dict:
    items = doc["datasets"][dataset]["entities"][entity]
    for item in items:
        if item["id"] == record_id:
            item["fields"][field] = value
            return doc
    raise KeyError(f"{dataset}/{entity}/{record_id} not found")


def build_json(source: dict | None = None, output: Path | None = None) -> dict:
    doc = source if source is not None else load_source()
    out = {
        "version": doc["version"],
        "updated": doc.get("updated"),
        "baseline": doc["datasets"]["baseline"]["entities"],
        "frontend_demo": doc["datasets"]["frontend_demo"]["entities"],
    }
    dst = Path(output) if output else DEFAULT_OUTPUT
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(
        json.dumps(out, ensure_ascii=False, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )
    return out


def _mapping_rules(source: dict | None = None) -> list[dict]:
    doc = source if source is not None else load_source()
    rules: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for ds_name, ds in doc["datasets"].items():
        if ds_name not in {"baseline", "teaching_simplified"}:
            continue
        for entity_name, items in ds["entities"].items():
            for item in items:
                if item.get("sync") is not True:
                    continue
                fields = item.get("fields", {})
                canonical_field = {
                    "departments": "dept_code",
                    "personnel": "certificate_number",
                    "workstations": "workstation_id",
                }.get(entity_name)
                for old in item.get("aliases", []) or []:
                    old_s = str(old)
                    new = ""
                    if canonical_field and re.fullmatch(r"[A-Z]\d+", old_s):
                        new = str(fields.get(canonical_field, item["id"]))
                    elif old_s in {"一号楼", "二号楼"}:
                        new = str(fields.get("address", ""))
                    elif old_s == "一中队" and entity_name == "departments":
                        new = str(fields.get("full_name", ""))
                    elif old_s == "二中队" and entity_name == "departments":
                        new = str(fields.get("full_name", ""))
                    elif old_s == "张三":
                        new = str(fields.get("name", ""))
                    elif old_s == "班长":
                        new = str(fields.get("rank", ""))
                    if new and new != old_s:
                        key = (old_s, new)
                        if key not in seen:
                            seen.add(key)
                            rules.append({
                                "old": old_s,
                                "new": new,
                                "dataset": ds_name,
                                "entity": entity_name,
                            })
    return rules


def _pattern(old: str) -> re.Pattern[str]:
    if re.fullmatch(r"[A-Za-z0-9_-]+", old):
        return re.compile(rf"(?<![A-Za-z0-9_]){re.escape(old)}(?![A-Za-z0-9_])")
    return re.compile(re.escape(old))


def _iter_files(root: Path):
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix not in SCAN_SUFFIXES:
            continue
        try:
            rel = p.relative_to(root)
        except ValueError:
            continue
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        if rel.parts[:2] == ("项目参考", "duty-historical"):
            continue
        if rel.parts and rel.parts[0] == "docs":
            continue
        if rel.as_posix() == "data/case_data.json":
            continue
        if rel.as_posix() == "tools/case_data.py":
            continue
        if rel.parts and rel.parts[0] == "tools" and rel.name.startswith("test_case_data_"):
            continue
        yield p, rel


def scan_aliases(root: Path | None = None, source: dict | None = None) -> list[dict]:
    base = Path(root) if root else ROOT
    rules = _mapping_rules(source)
    hits: list[dict] = []
    compiled = [(rule, _pattern(rule["old"])) for rule in rules]
    for path, rel in _iter_files(base):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for rule, pat in compiled:
            for m in pat.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                hits.append({
                    "file": rel.as_posix(),
                    "line": line_no,
                    "old": rule["old"],
                    "new": rule["new"],
                    "context": text[max(0, m.start() - 30):m.end() + 30].replace("\n", " "),
                })
    return hits


def apply_changes(root: Path | None = None, yes: bool = False, source: dict | None = None) -> list[dict]:
    base = Path(root) if root else ROOT
    hits = scan_aliases(base, source)
    by_file: dict[str, list[dict]] = {}
    for h in hits:
        by_file.setdefault(h["file"], []).append(h)
    changes: list[dict] = []
    rules = {(h["old"], h["new"]): _pattern(h["old"]) for h in hits}
    for rel, file_hits in by_file.items():
        path = base / rel
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        newline = "\r\n" if b"\r\n" in raw else "\n"
        normalized = text.replace("\r\n", "\n")
        new_text = normalized
        for (old, new), pat in sorted(rules.items(), key=lambda item: len(item[0][0]), reverse=True):
            new_text = pat.sub(new, new_text)
        if new_text != normalized:
            if yes:
                path.write_bytes(new_text.replace("\n", newline).encode("utf-8"))
            changes.append({
                "file": rel,
                "old": ",".join(sorted({h["old"] for h in file_hits})),
                "new": ",".join(sorted({h["new"] for h in file_hits})),
                "old_text": normalized,
                "new_text": new_text,
                "hits": file_hits,
            })
    return changes


def check_report(root: Path | None = None) -> dict:
    base = Path(root) if root else ROOT
    hits = scan_aliases(base)
    history: list[dict] = []
    docs = base / "docs"
    if docs.exists():
        rules = _mapping_rules()
        for path in docs.rglob("*"):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for rule in rules:
                if re.search(rf"(?<![A-Za-z0-9_]){re.escape(rule['old'])}", text):
                    history.append({
                        "area": "docs",
                        "file": path.relative_to(base).as_posix(),
                        "old": rule["old"],
                    })
                    break
    return {"active_unmatched": hits, "history": history}


def _cmd_show(args: argparse.Namespace) -> int:
    doc = load_source()
    for ds_name, ds in doc["datasets"].items():
        print(f"[{ds_name}] {ds.get('description', '')}")
        for entity, items in ds["entities"].items():
            print(f"  {entity}: {len(items)}")
    return 0


def _cmd_set(args: argparse.Namespace) -> int:
    doc = load_source()
    value = args.value
    if args.field in {"is_active"}:
        value = int(value)
    set_field(doc, args.dataset, args.entity, args.id, args.field, value)
    save_source(doc)
    print(f"updated {args.dataset}/{args.entity}/{args.id}.{args.field} = {value}")
    return 0


def _cmd_build(args: argparse.Namespace) -> int:
    out = build_json()
    print(f"wrote {DEFAULT_OUTPUT.relative_to(ROOT)} (version {out['version']})")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    report = check_report()
    print(f"active_unmatched: {len(report['active_unmatched'])}")
    for h in report["active_unmatched"][:20]:
        print(f"  {h['file']}:{h['line']} {h['old']} -> {h['new']}")
    print(f"history(docs): {len(report['history'])}")
    return 0


def _print_changes(changes: list[dict]) -> None:
    for c in changes:
        print(f"{c['file']}: {len(c['hits'])} replacement(s)")
        for h in c["hits"][:5]:
            print(f"  L{h['line']}: {h['old']} -> {h['new']}  | {h['context'][:80]}")


def _cmd_diff(args: argparse.Namespace) -> int:
    changes = apply_changes(yes=False)
    print(f"dry-run: {len(changes)} file(s) would change")
    _print_changes(changes)
    return 0


def _cmd_apply(args: argparse.Namespace) -> int:
    if not args.yes:
        return _cmd_diff(args)
    changes = apply_changes(yes=True)
    print(f"applied: {len(changes)} file(s)")
    _print_changes(changes)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show").set_defaults(func=_cmd_show)
    p_set = sub.add_parser("set")
    p_set.add_argument("dataset")
    p_set.add_argument("entity")
    p_set.add_argument("id")
    p_set.add_argument("field")
    p_set.add_argument("value")
    p_set.set_defaults(func=_cmd_set)
    sub.add_parser("build").set_defaults(func=_cmd_build)
    sub.add_parser("check").set_defaults(func=_cmd_check)
    sub.add_parser("diff").set_defaults(func=_cmd_diff)
    p_apply = sub.add_parser("apply")
    p_apply.add_argument("--yes", action="store_true")
    p_apply.set_defaults(func=_cmd_apply)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
