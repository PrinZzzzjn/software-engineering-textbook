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


def test_seed_constants_use_canonical_ids():
    p = Path("项目参考/duty-simplified/main.py")
    text = p.read_text(encoding="utf-8")
    assert 'D01"' not in text
    assert "D001" in text
