from pathlib import Path


def test_all_seed_projects_have_loader():
    roots = []
    for p in Path("实训工程参考").glob("实训*/项目/main.py"):
        if "_seed_" in p.read_text(encoding="utf-8"):
            roots.append(p)
    assert roots
    for p in roots:
        text = p.read_text(encoding="utf-8")
        assert "case_data.json" in text or "load_case_data" in text
        assert "_load_case_data()" in text


def test_seed_reads_generated_json_values():
    import json

    data = json.loads(Path("data/case_data.json").read_text(encoding="utf-8"))
    dept_fields = data["baseline"]["departments"][0]["fields"]
    source = Path("实训工程参考/实训10-1/项目/main.py").read_text(encoding="utf-8")
    assert "for code, name, address in _seed_rows(" in source
    assert 'DATA.get("baseline", {}).get("departments", [])' in source
    assert dept_fields["dept_code"] == "D001"


def test_seed_constants_use_canonical_ids():
    p = Path("项目参考/duty-simplified/main.py")
    text = p.read_text(encoding="utf-8")
    assert 'D' + '01"' not in text
    assert "D001" in text
