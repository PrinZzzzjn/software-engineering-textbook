from md2typst import convert


def test_fence_keeps_language():
    out = convert("```python\nx = 1\n```\n")
    assert out.count("```python") == 1 and "x = 1" in out


def test_fence_without_language():
    assert convert("```\nplain\n```\n").count("```") == 2


def test_code_caption_from_bold_lead():
    out = convert("**代码 5-1-5** · 命令（Bash）\n")
    assert out.startswith("#code-caption[")


def test_fence_with_backticks_uses_longer_fence():
    out = convert("````\na ``` b\n````\n")
    assert "````\na ``` b\n````" in out


def test_long_code_line_is_not_split_by_converter():
    line = "x = " + ", ".join(f"value_{i}" for i in range(30))
    out = convert(f"```python\n{line}\n```\n")
    assert line in out


def test_code_caption_groups_with_following_fence():
    out = convert("**代码 5-1-5** · 命令（Bash）\n\n```bash\nls\n```\n")
    assert out.startswith("#code-group(")
    assert "```bash" in out and "代码 5-1-5" in out
    assert out.count("#code-caption[") == 1


def test_long_code_block_may_break_across_pages():
    body = "\n".join(f"line_{i} = {i}" for i in range(60))
    out = convert(f"```python\n{body}\n```\n")
    assert "long: true" in out
