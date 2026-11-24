from pathlib import Path

from case_data import ROOT, apply_changes, load_source


def test_mapped_field_changes_propagate_to_diff(tmp_path):
    source = tmp_path / "case_data.yaml"
    source.write_text(
        """version: 1
updated: 2026-11-24
description: fixture
datasets:
  baseline:
    entities:
      departments:
        - id: D001
          fields: {dept_code: D001, full_name: 一中队, address: 一号营区}
          aliases: [D01, 一号楼, 一中队]
          used_in: [fixture]
          sync: true
  teaching_simplified: {description: none, entities: {}}
  verification: {description: none, entities: {}}
  frontend_demo: {description: none, entities: {}}
""",
        encoding="utf-8",
    )
    doc = load_source(source)
    doc["datasets"]["baseline"]["entities"]["departments"][0]["fields"]["full_name"] = "新中队"
    work = tmp_path / "work"
    work.mkdir()
    (work / "x.md").write_text("D01 对应一中队", encoding="utf-8")
    changes = apply_changes(work, yes=False, source=doc)
    assert changes
    assert "新中队" in changes[0]["new_text"]
