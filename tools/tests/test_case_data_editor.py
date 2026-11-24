from pathlib import Path

import yaml
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "case_data_editor" / "app.py")


def test_editor_shows_datasets_and_actions():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert "执勤电子年鉴" in at.title[0].value
    labels = [b.label for b in at.button]
    assert any("检查引用" in label for label in labels)


def test_editor_can_select_entity_and_change_field(tmp_path):
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
          aliases: [D01]
          used_in: [fixture]
          sync: true
  teaching_simplified: {description: none, entities: {}}
  verification: {description: none, entities: {}}
  frontend_demo: {description: none, entities: {}}
""",
        encoding="utf-8",
    )
    at = AppTest.from_file(APP, default_timeout=30)
    at.query_params["source"] = str(source)
    at = at.run()
    assert not at.exception
    at.text_input(key="edit_baseline_departments_D001_address").set_value("测试营区").run()
    at.button(key="save_field").click().run()
    assert not at.exception
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    assert doc["datasets"]["baseline"]["entities"]["departments"][0]["fields"]["address"] == "测试营区"
    assert any("已保存" in s.value for s in at.success)
