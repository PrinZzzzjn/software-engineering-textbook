from md2typst import convert


def test_table_with_alignment():
    md = "| 步骤 | 输入 |\n| --- | ---: |\n| 1 | 需求 |\n"
    out = convert(md)
    assert "table(" in out and "columns: (" in out and "align: (left, right)" in out


def test_pseudo_heading_from_bold_paragraph():
    assert convert("**顺序的依据**\n").startswith("#pseudo-heading[顺序的依据]")


def test_blockquote_becomes_callout():
    assert "#callout[" in convert("> 提示：先备份。\n")


def test_figure_caption_detected():
    out = convert("*图 4-1：从需求到结构的设计翻译链*\n")
    assert "#fig-caption[图 4-1：从需求到结构的设计翻译链]" in out


def test_nested_bullet_list():
    out = convert("- 一\n  - 二\n")
    assert out.count("- ") == 2 and "  - 二" in out


def test_horizontal_rule_does_not_leak_markdown():
    out = convert("前文\n\n---\n\n后文\n")
    assert "---" not in out


def test_paragraph_with_inline_bold_stays_a_paragraph():
    out = convert("**耦合**指模块之间的依赖。**内聚**指模块内部的联系。\n")
    assert "#pseudo-heading" not in out
    assert "*耦合*" in out


def test_mermaid_tall_diagram_is_height_capped():
    out = convert(
        "```mermaid\ngraph TD\nA-->B\n```\n",
        resolve_mermaid=lambda block: ("/x.svg", 300.0, 1600.0),
    )
    assert "height: 185mm" in out


def test_mermaid_narrow_diagram_keeps_text_sized_to_body():
    out = convert(
        "```mermaid\ngraph TD\nA-->B\n```\n",
        resolve_mermaid=lambda block: ("/x.svg", 168.0, 618.0),
    )
    # 按 0.13 mm/px 缩放：168 px ≈ 22 mm 宽，而不是撑满版心
    assert "width: 22mm" in out


def test_mermaid_caption_is_grouped_with_image():
    out = convert(
        "```mermaid\ngraph TD\nA-->B\n```\n\n*图 5-1：一条链*\n",
        resolve_mermaid=lambda block: ("/x.svg", 600.0, 200.0),
    )
    assert "#fig-group[" in out
    assert "#fig-caption[图 5-1：一条链]" in out


def test_task_items_become_checkboxes():
    out = convert("- [ ] 第一条\n- [x] 第二条\n")
    assert "#task-list[" in out
    assert "□ 第一条" in out and "■ 第二条" in out


def test_pseudo_headings_numbered_within_numbered_section():
    md = "## 8.1 数据写入\n\n**六个文件的分工**\n\n正文。\n\n**另一个小标题**\n"
    out = convert(md)
    assert '#pseudo-heading(number: "8.1.1")[六个文件的分工]' in out
    assert '#pseudo-heading(number: "8.1.2")[另一个小标题]' in out


def test_pseudo_heading_unnumbered_outside_numbered_section():
    md = "## 本章要解决的问题\n\n**一个能跑起来的程序，和一个可以交付的系统，差什么？**\n"
    out = convert(md)
    assert "#pseudo-heading[一个能跑起来的程序" in out


def test_bold_sentence_ending_with_period_is_not_a_heading():
    md = "## 2.5 MoSCoW 优先级\n\n**推广阶段的截止日期：第 3 周前完成哪些项目可进接口冻结。**\n"
    out = convert(md)
    assert "#pseudo-heading" not in out
    assert "*推广阶段的截止日期" in out


def test_pseudo_heading_with_inline_code_is_a_heading():
    md = "## 4.6 六文件最小实现\n\n**用 `Depends` 注入查询参数**\n"
    out = convert(md)
    assert '#pseudo-heading(number: "4.6.1")[用 `Depends` 注入查询参数]' in out


def test_two_bold_runs_are_not_a_heading():
    md = "## 4.6 六文件最小实现\n\n**甲**中间文字**乙**\n"
    assert "#pseudo-heading" not in convert(md)
