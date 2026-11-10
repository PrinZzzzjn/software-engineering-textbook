"""界面主题与可复用布局组件。

教学要点（对应课次 21「前端视觉优化」）：
- 页面的"高级感"主要来自三件事：统一配色、卡片分组、留白；
- 把重复的标题/卡片/提示封装成函数，页面代码更干净；
- 图表颜色不是随手取的，而是与主题一致并通过对比度校验。

配色说明：
- 主色 #0F766E（teal-700）用于按钮、链接；
- 图表系列色 #0D9488（teal-600），已在白底与 #F8FAFC 底上校验：
  亮度带、色度下限、对比度均达标（对比度 >= 3:1）。
"""

import html

import streamlit as st

# 主题色（与 .streamlit/config.toml 保持一致）
PRIMARY = "#0F766E"
CHART_COLOR = "#0D9488"
INK = "#0F172A"
MUTED = "#64748B"

_CSS = """
<style>
  /* 页面留白：宽屏下内容不贴边 */
  .block-container { padding-top: 2.2rem; padding-bottom: 2.5rem; max-width: 1180px; }
  h1, h2, h3 { letter-spacing: -0.01em; }

  /* 首页顶部渐变横幅 */
  .duty-hero {
      background: linear-gradient(120deg, #0F766E 0%, #0D9488 55%, #14B8A6 100%);
      color: #ffffff;
      border-radius: 18px;
      padding: 30px 34px;
      margin-bottom: 20px;
      box-shadow: 0 8px 24px rgba(13, 148, 136, 0.18);
  }
  .duty-hero h1 { color: #ffffff; margin: 0 0 8px 0; font-size: 1.9rem; }
  .duty-hero p  { color: rgba(255, 255, 255, 0.92); margin: 0; font-size: 1rem; }
  .duty-badge {
      display: inline-block; margin-top: 14px; padding: 3px 12px;
      border-radius: 999px; background: rgba(255, 255, 255, 0.18);
      color: #ffffff; font-size: 0.8rem;
  }

  /* 功能卡片 */
  .duty-card {
      background: #ffffff;
      border: 1px solid rgba(15, 23, 42, 0.08);
      border-radius: 16px;
      padding: 18px 20px;
      height: 100%;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
  }
  .duty-card h3 { margin: 0 0 8px 0; font-size: 1.02rem; color: #0F172A; }
  .duty-card p  { color: #64748B; margin: 0; font-size: 0.9rem; line-height: 1.6; }
</style>
"""


def inject_css() -> None:
    """在页面顶部注入统一 CSS。每个页面调用一次即可，重复调用不会重复生效。"""
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = "") -> None:
    """统一的页面标题区：标题 + 一句说明。"""
    st.markdown(f"## {icon} {title}".strip())
    if subtitle:
        st.caption(subtitle)


def hero(title: str, subtitle: str, badge: str = "") -> None:
    """首页顶部渐变横幅。"""
    badge_html = (
        f'<span class="duty-badge">{html.escape(badge)}</span>' if badge else ""
    )
    st.markdown(
        f'<div class="duty-hero"><h1>{html.escape(title)}</h1>'
        f"<p>{html.escape(subtitle)}</p>{badge_html}</div>",
        unsafe_allow_html=True,
    )


def feature_card(title: str, body: str, icon: str = "") -> None:
    """一张功能说明卡片，配合 st.columns 使用。"""
    st.markdown(
        f'<div class="duty-card"><h3>{icon} {html.escape(title)}</h3>'
        f"<p>{html.escape(body)}</p></div>",
        unsafe_allow_html=True,
    )


def set_flash(message: str) -> None:
    """把提示消息暂存到 session_state，供 rerun 之后显示。"""
    st.session_state["_flash"] = message


def show_flash() -> None:
    """显示并清除上一次操作留下的提示消息。"""
    message = st.session_state.pop("_flash", None)
    if message:
        st.toast(message, icon="✅")
