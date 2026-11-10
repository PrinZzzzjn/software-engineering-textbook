"""登录、登出与页面访问控制。

教学要点（对应课次 19、20）：
- Streamlit 每次交互都会从头重跑脚本，所以"登录状态"必须放在 st.session_state；
- 每个页面顶部调用 require_login()，未登录时显示登录框并 st.stop()，
  这样即使用户直接输入页面 URL，也进不去；
- 登录成功后调用 st.rerun()，让页面带着登录态重新渲染。
"""

import streamlit as st

import api_client as api
import ui


def current_user() -> dict:
    return st.session_state.get("current_user", {})


def is_logged_in() -> bool:
    return bool(st.session_state.get("access_token"))


def render_login() -> None:
    """渲染登录表单；登录成功后刷新页面。"""
    ui.inject_css()
    st.markdown("<div style='height:6vh'></div>", unsafe_allow_html=True)

    # 居中一列，形成"登录卡片"的视觉效果
    left, middle, right = st.columns([1, 1.15, 1])
    with middle:
        with st.container(border=True):
            st.markdown("## 🗂️ 值班数据统计系统")
            st.caption("专题三参考实现 · 请使用系统账号登录")

            with st.form("login_form"):
                username = st.text_input("用户名", value="admin")
                password = st.text_input("密码", type="password")
                submitted = st.form_submit_button(
                    "登 录",
                    width="stretch",
                    type="primary",
                )

            if submitted:
                if not username or not password:
                    st.error("请输入用户名和密码")
                    return
                try:
                    with st.spinner("正在登录..."):
                        api.login(username, password)
                except api.ApiError as exc:
                    st.error(exc.detail)
                    return
                st.rerun()


def require_login() -> None:
    """页面访问守卫：未登录则显示登录框并停止渲染当前页面。"""
    if not is_logged_in():
        st.warning("请先登录后再访问该页面")
        render_login()
        st.stop()


def render_user_box() -> None:
    """在侧边栏显示当前用户与退出按钮。"""
    user = current_user()
    if not user:
        return

    with st.sidebar:
        st.markdown("### 🗂️ 值班数据统计")
        st.caption("专题三参考实现")
        st.divider()
        st.caption(f"当前用户：{user.get('username', '-')}")
        st.caption(f"角色：{user.get('role', '-')}")
        if st.button("退出登录", width="stretch"):
            st.session_state.clear()
            st.rerun()
