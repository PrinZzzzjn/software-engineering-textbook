import subprocess

from build import TYPST, compile_typ, WORK_DIR


def test_minimal_book_compiles():
    src = WORK_DIR / "smoke.typ"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(
        '#import "/tools/print/style.typ": *\n'
        "#show: template\n"
        '#chapter("第 1 章", "冒烟测试")\n'
        "正文一段，中文排版，用来确认宋体字形、首行缩进与行距。\n"
        "#pseudo-heading[顺序的依据]\n再见。\n"
        "#pagebreak()\n第二页正文，用来确认偶数页页眉与页码。\n",
        encoding="utf-8",
    )
    out = WORK_DIR / "smoke.pdf"
    compile_typ(src, out)
    assert out.exists() and out.stat().st_size > 3000
    assert subprocess.run([str(TYPST), "--version"], capture_output=True).returncode == 0
