from pathlib import Path

SOURCE_TEXT = """version: 1
updated: 2026-11-24
description: fixture
datasets:
  baseline:
    entities:
      departments:
        - id: D001
          fields: {dept_code: D001, full_name: 一中队, address: 一号营区}
          aliases: [D01, 一号楼]
          used_in: [fixture]
          sync: true
"""


def test_load_and_set_field(tmp_path):
    from case_data import load_source, set_field

    src = tmp_path / "case_data.yaml"
    src.write_text(SOURCE_TEXT, encoding="utf-8")
    doc = load_source(src)
    updated = set_field(doc, "baseline", "departments", "D001", "address", "新地址")
    assert updated["datasets"]["baseline"]["entities"]["departments"][0]["fields"]["address"] == "新地址"


def test_scan_aliases_finds_whole_word_only(tmp_path):
    from case_data import scan_aliases

    p = tmp_path / "x.md"
    p.write_text("旧值 D01 与 D010 和 D001 同时出现", encoding="utf-8")
    hits = scan_aliases(tmp_path)
    d01_hits = [h for h in hits if h["old"] == "D01"]
    assert len(d01_hits) == 1
    assert d01_hits[0]["new"] == "D001"


def test_apply_dry_run_returns_changes_without_writing(tmp_path):
    from case_data import apply_changes

    p = tmp_path / "x.md"
    original = "使用 D01 作为单位编码"
    p.write_text(original, encoding="utf-8")
    changes = apply_changes(tmp_path, yes=False)
    assert changes
    assert any(c["old"] == "D01" and c["new"] == "D001" for c in changes)
    assert p.read_text(encoding="utf-8") == original
