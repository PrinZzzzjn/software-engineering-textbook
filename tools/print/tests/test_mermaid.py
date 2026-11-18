from mermaid_render import collect_blocks, hash_block, image_size, render


def test_collect_blocks():
    md = "前文\n```mermaid\nflowchart LR\n  A --> B\n```\n后文\n"
    assert collect_blocks(md) == ["flowchart LR\n  A --> B"]


def test_collect_blocks_ignores_info_suffix():
    md = "```mermaid title\nflowchart LR\n  A --> B\n```\n"
    assert collect_blocks(md) == ["flowchart LR\n  A --> B"]


def test_hash_is_stable():
    assert hash_block("a") == hash_block("a") != hash_block("b")


def test_render_and_cache(tmp_path):
    block = "flowchart LR\n  A[需求] --> B[表结构]"
    p1 = render(block, tmp_path)
    assert p1.exists() and p1.stat().st_size > 1000
    mtime = p1.stat().st_mtime_ns
    p2 = render(block, tmp_path)
    assert p2 == p1 and p2.stat().st_mtime_ns == mtime


def test_svg_has_no_foreign_object(tmp_path):
    p = render("flowchart LR\n  A --> B", tmp_path)
    assert p.suffix == ".svg"
    assert "foreignObject" not in p.read_text(encoding="utf-8")


def test_image_size_reads_svg_dimensions(tmp_path):
    p = render("flowchart LR\n  A --> B", tmp_path)
    width, height = image_size(p)
    assert width > 0 and height > 0


def test_cache_key_tracks_render_config(tmp_path, monkeypatch):
    import mermaid_render

    block = "flowchart LR\n  A --> B"
    first = mermaid_render.render(block, tmp_path)
    config = tmp_path / "alt-mermaid.json"
    config.write_text('{"theme": "neutral", "htmlLabels": false}', encoding="utf-8")
    monkeypatch.setattr(mermaid_render, "MERMAID_CONFIG", config)
    second = mermaid_render.render(block, tmp_path)
    assert second != first
