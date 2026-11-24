from pathlib import Path

from case_data import apply_changes


def test_apply_uses_boundary_matching_on_write(tmp_path):
    p = tmp_path / "x.md"
    original = "D010 D01 /departments/D01 D404 D99 D001"
    p.write_text(original, encoding="utf-8")
    apply_changes(tmp_path, yes=True)
    assert p.read_text(encoding="utf-8") == "D010 D001 /departments/D001 D404 D99 D001"
