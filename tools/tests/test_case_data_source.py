from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "case_data.yaml"


def test_source_exists_and_has_four_datasets():
    assert SRC.exists()
    doc = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    assert doc["version"] == 1
    assert set(doc["datasets"]) == {
        "baseline",
        "teaching_simplified",
        "verification",
        "frontend_demo",
    }


def test_baseline_records_are_complete():
    doc = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    baseline = doc["datasets"]["baseline"]["entities"]
    assert [r["id"] for r in baseline["departments"]] == ["D001", "D002"]
    assert [r["id"] for r in baseline["personnel"]] == ["P001", "P002"]
    assert [r["id"] for r in baseline["workstations"]] == ["W001", "W002"]
    assert len(baseline["duty_records"]) == 4
    assert baseline["users"][0]["fields"]["username"] == "admin"


def test_aliases_and_sync_strategy_are_present():
    doc = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    dept = doc["datasets"]["baseline"]["entities"]["departments"][0]
    assert "D01" in dept["aliases"]
    assert dept["fields"]["address"] == "人民路1号"
    assert dept["fields"]["full_name"] == "一中队"
