"""表格与分页的可复用组件。

教学要点（教材 17.2）：
- 「表格 + 分页」在单位、人员、统计等页面反复出现，同一段界面代码出现第二次再抽；
- 抽成组件后，页面只关心「取哪些字段、传哪些查询参数」；
- 分页由后端完成（传 page / page_size），前端只负责展示当前页和翻页按钮。
"""

from __future__ import annotations

import math
from typing import Iterable

import pandas as pd
import streamlit as st


def render_table(
    items: Iterable[dict],
    columns: list[str] | None = None,
    column_config: dict | None = None,
) -> None:
    """把接口返回的 items 渲染成表格。

    columns       指定展示字段和顺序；
    column_config 用于把英文字段名换成中文表头（见第 15 章）。
    """
    rows = list(items)
    if not rows:
        st.info("暂无数据")
        return

    df = pd.DataFrame(rows)
    if columns:
        df = df[[c for c in columns if c in df.columns]]
    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        column_config=column_config,
    )


def pagination_bar(total: int, page: int, page_size: int, key: str) -> int:
    """渲染「上一页 / 第 x / y 页 / 下一页」，返回用户点击后的页码。

    调用方负责把返回值写回 session_state 并在变化时 st.rerun()。
    """
    pages = max(1, math.ceil(total / page_size)) if total else 1
    page = min(max(page, 1), pages)

    left, middle, right = st.columns([1, 2, 1])
    with left:
        if st.button(
            "上一页",
            key=f"{key}_prev",
            disabled=page <= 1,
            width="stretch",
        ):
            page -= 1
    with middle:
        st.markdown(
            "<div style='text-align:center;padding-top:0.4rem;'>"
            f"第 {page} / {pages} 页，共 {total} 条"
            "</div>",
            unsafe_allow_html=True,
        )
    with right:
        if st.button(
            "下一页",
            key=f"{key}_next",
            disabled=page >= pages,
            width="stretch",
        ):
            page += 1
    return page
