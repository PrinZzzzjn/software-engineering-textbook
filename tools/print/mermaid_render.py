"""把 Markdown 里的 mermaid 代码块渲染成矢量图，按内容哈希缓存。

用本机 Edge 当无头浏览器（避免下载 Chromium），输出 SVG；
若 SVG 里出现 Typst 不支持的 foreignObject，退回 300 dpi 级别的 PNG。
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN = REPO_ROOT / "build" / "pdf-toolchain"
MMDC = TOOLCHAIN / "node_modules" / "@mermaid-js" / "mermaid-cli" / "src" / "cli.js"
PPTR_CONFIG = TOOLCHAIN / "pptr.json"
MERMAID_CONFIG = TOOLCHAIN / "mermaid.json"

_BLOCK_RE = re.compile(r"```mermaid[^\n]*\n(.*?)```", re.DOTALL)
_SIZE_RE = re.compile(r'<svg[^>]*?width="([0-9.]+)(?:px)?"[^>]*?height="([0-9.]+)(?:px)?"')
_VIEWBOX_RE = re.compile(r'viewBox="([-0-9.]+)\s+([-0-9.]+)\s+([0-9.]+)\s+([0-9.]+)"')


def collect_blocks(text: str) -> list[str]:
    """取出文本中所有 mermaid 代码块的内容。"""
    return [match.group(1).strip("\n") for match in _BLOCK_RE.finditer(text)]


def hash_block(block: str) -> str:
    return hashlib.sha1(block.strip().encode("utf-8")).hexdigest()[:16]


def _config_signature() -> str:
    """配置（主题、字号、浏览器参数）变了，缓存必须失效。"""
    payload = b""
    for path in (MERMAID_CONFIG, PPTR_CONFIG):
        try:
            payload += path.read_bytes()
        except OSError:
            continue
    return hashlib.sha1(payload).hexdigest()[:8]


def image_size(path: Path) -> tuple[float, float]:
    """读出 SVG 的固有尺寸（像素）。

    有的图（如 classDiagram）宽高写成 100% + max-width，只有 viewBox 是真尺寸，
    按像素匹配会失败，这里回退到 viewBox，避免整张图被拉满版心。
    """
    if path.suffix != ".svg":
        return (0.0, 0.0)
    markup = path.read_text(encoding="utf-8")
    match = _SIZE_RE.search(markup)
    if match:
        return (float(match.group(1)), float(match.group(2)))
    view = _VIEWBOX_RE.search(markup)
    if view:
        return (float(view.group(3)), float(view.group(4)))
    return (0.0, 0.0)


def _run_mmdc(source: Path, target: Path, *, png: bool = False) -> None:
    args = [
        "node",
        str(MMDC),
        "-p",
        str(PPTR_CONFIG),
        "-c",
        str(MERMAID_CONFIG),
        "-i",
        str(source),
        "-o",
        str(target),
        "-b",
        "white" if png else "transparent",
        "-q",
    ]
    if png:
        args += ["-s", "3"]
    subprocess.run(args, check=True, cwd=TOOLCHAIN)


def render(block: str, out_dir: Path) -> Path:
    """渲染单个 mermaid 块，命中缓存直接返回；返回 .svg（或回退的 .png）。"""
    digest = f"{hash_block(block)}-{_config_signature()}"
    svg = out_dir / f"{digest}.svg"
    png = out_dir / f"{digest}.png"
    if svg.exists():
        return svg
    if png.exists():
        return png

    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "diagram.mmd"
        source.write_text(block, encoding="utf-8")
        target = Path(tmp) / "diagram.svg"
        _run_mmdc(source, target)
        markup = target.read_text(encoding="utf-8")
        if "foreignObject" in markup:
            fallback = Path(tmp) / "diagram.png"
            _run_mmdc(source, fallback, png=True)
            shutil.move(str(fallback), png)
            return png
        shutil.move(str(target), svg)
        return svg


def render_all(blocks: list[str], out_dir: Path) -> dict[str, Path]:
    """批量渲染，返回 哈希 → 图片路径 的映射。"""
    return {hash_block(block): render(block, out_dir) for block in blocks}
