from build import PRINT_DIR, book_typst


def test_all_chapters_present():
    src = book_typst()
    assert src.count("#chapter(") == 24
    assert "附录 A" in src and "附录 B" in src and "附录 C" in src


def test_front_matter_and_toc():
    src = book_typst()
    style = (PRINT_DIR / "style.typ").read_text(encoding="utf-8")
    assert "#toc-page()" in src
    assert "outline(" in style and 'numbering("i"' in style
    assert "00-教材设计" not in src


def test_manual_toc_section_dropped():
    src = book_typst()
    # 手写目录里的章条目（自动目录不含课次/学时描述）
    assert "课次 1 · 2 学时理论" not in src
    assert "第 1 章 软件工程基本概念 — 课次" not in src


def test_four_parts_present():
    src = book_typst()
    assert src.count("#part(") == 4
    assert "第一篇" in src and "第四篇" in src


def test_editorial_notes_dropped():
    src = book_typst()
    assert "编排位置" not in src
    assert "不可直接投入课堂" not in src


def test_mermaid_becomes_image():
    src = book_typst()
    assert "#fig-image(" in src
    assert "```mermaid" not in src


def test_cli_produces_all_outputs(tmp_path):
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "tools/print/build.py", "--all", "--out", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=2400,
        cwd=str(PRINT_DIR.parents[1]),
    )
    assert result.returncode == 0, result.stderr[-2000:]
    book = tmp_path / "软件工程实践-2.0-送审样书.pdf"
    assert book.stat().st_size > 1_000_000
    chapters = sorted((tmp_path / "分章").glob("*.pdf"))
    assert len(chapters) == 24
    assert chapters[0].name.startswith("第01章-")
    assert len(list((tmp_path / "预览").glob("*.png"))) == 8
    assert (tmp_path / "排版说明.md").exists()

    from pypdf import PdfReader

    reader = PdfReader(str(book))
    # 卷首用罗马数字，第一张正文页（封面之后）应印 i
    assert (reader.pages[1].extract_text() or "").strip().endswith("i")
