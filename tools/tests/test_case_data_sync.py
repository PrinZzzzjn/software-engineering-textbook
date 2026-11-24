from case_data import ROOT, check_report, scan_aliases

LEGACY = {"D01", "P01", "W01", "一号楼", "张三", "班长"}


def test_no_legacy_ids_in_active_content():
    hits = scan_aliases(ROOT)
    legacy = [h for h in hits if h["old"] in LEGACY]
    assert legacy == []


def test_check_reports_history_separately():
    report = check_report(ROOT)
    assert report["active_unmatched"] == []
    assert any(item["area"] == "docs" for item in report["history"])
