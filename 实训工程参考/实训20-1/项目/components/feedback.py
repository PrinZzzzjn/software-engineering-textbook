"""操作反馈（flash message）组件。

教学要点（教材 18.3）：
- `st.success` 画在当前这次渲染上，紧接着的 `st.rerun()` 会丢掉它；
- 先把消息暂存进 `session_state`，重跑后由 `show_flash()` 取出并显示一次；
- 取出即清除，避免每次重跑都重复提示。
"""

import streamlit as st


def set_flash(message: str) -> None:
    """暂存一条操作反馈，等下一次渲染再显示。"""
    st.session_state["_flash"] = message


def show_flash() -> None:
    """取出并显示一次操作反馈；没有消息时不显示。"""
    message = st.session_state.pop("_flash", None)
    if message:
        st.toast(message, icon="✅")
