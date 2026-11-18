from md2typst import convert, escape


def test_escape_specials():
    assert escape("a#b*c_d$e<f>g@h~i`j[") == r"a\#b\*c\_d\$e\<f\>g\@h\~i\`j\["


def test_heading_levels_preserved():
    assert convert("## 4.1 需求\n").startswith("== 4.1 需求")
    assert convert("#### 例 13-1：标题\n").startswith("==== 例 13-1：标题")


def test_inline_code_and_emphasis():
    assert "`Depends`" in convert("用 `Depends` 注入。")
    assert "*粗*" in convert("这句里的**粗**体") and "_斜_" in convert("这句里的*斜*体")


def test_links_render_as_text_for_local_paths():
    out = convert("[术语表](术语表.md)")
    assert "术语表" in out and "术语表.md" not in out


def test_paragraph_blank_line_separated():
    out = convert("第一段。\n\n第二段。\n")
    assert out.count("\n\n") == 1
