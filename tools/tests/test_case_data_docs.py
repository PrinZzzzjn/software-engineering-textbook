from pathlib import Path


def test_usage_doc_exists_and_covers_commands():
    p = Path("docs/案例数据管理使用说明.md")
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    for token in [
        "tools/case_data.py show",
        "tools/case_data.py set",
        "streamlit run tools/case_data_editor/app.py",
        "apply --yes",
    ]:
        assert token in text
