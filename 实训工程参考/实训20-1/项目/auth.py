"""登录、登出与页面访问守卫。

教学要点（教材 17.2、17.5）：
- 登录状态放在 st.session_state：Streamlit 每次交互都会从头重跑脚本；
- 守卫逻辑只写一次，各子页面顶部调用 require_login()；
- 前端守卫只解决体验，真正的权限边界仍由后端校验。
"""

import streamlit as st

import api_client as api
from components.errors import show_api_error


def current_user() -> dict:
    return st.session_state.get("current_user", {})


def is_logged_in() -> bool:
    return bool(st.session_state.get("access_token"))


def render_login() -> None:
    """渲染登录表单；登录成功后写入令牌并重跑页面。"""
    st.title("🗂️ 执勤电子年鉴")
    st.caption("请使用系统账号登录（演示账号 admin / admin123）")

    notice = st.session_state.pop("login_notice", None)
    if notice:
        st.warning(notice)

    with st.form("login_form"):
        username = st.text_input("用户名", value="admin", key="login_username")
        password = st.text_input("密码", type="password", key="login_password")
        submitted = st.form_submit_button("登录", type="primary", key="login_submit")

    if not submitted:
        return
    if not username or not password:
        st.error("请输入用户名和密码")
        return

    try:
        data = api.post(
            "/users/login",
            json={"username": username, "password": password},
        )
    except api.ApiError as exc:
        # 这里的 401 是账号或密码错误，不是令牌过期
        st.error("用户名或密码错误" if exc.status_code == 401 else exc.detail)
        return

    st.session_state["access_token"] = data["access_token"]
    st.session_state["current_user"] = data.get("user", {})
    st.rerun()


def require_login() -> None:
    """页面访问守卫：未登录时提示并停止渲染当前页面。"""
    if not is_logged_in():
        st.warning("请先登录后再访问该页面")
        render_login()
        st.stop()


def render_user_box() -> None:
    """在侧边栏显示当前用户、后端状态与退出按钮。"""
    user = current_user()
    if not user:
        return

    with st.sidebar:
        st.divider()
        st.caption(f"当前用户：{user.get('username', '-')}")
        st.caption(f"角色：{user.get('role', '-')}")
        try:
            status = api.get("/health")
            st.success(f"后端正常：{status.get('status', 'ok')}")
        except api.ApiError as exc:
            # 侧边栏连通性提示也走统一映射，连接失败时给出可读原因
            show_api_error(exc)
        if st.button("退出登录", width="stretch", key="logout"):
            st.session_state.clear()
            st.rerun()
