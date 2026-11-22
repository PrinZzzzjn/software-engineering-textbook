"""实训 16-1 单位管理页：数据读取与展示（接真实后端）。

启动（在本目录下）：
    python -m streamlit run app.py

前提：后端运行在 http://127.0.0.1:8000（实训 13-1 项目），演示账号 admin / admin123。
本页把 15-1 的假数据换成 GET /departments，新增改为 POST /departments；
加载、空、错误三种状态分别用 spinner、st.info、st.error + st.stop 处理。
"""

import pandas as pd
import streamlit as st

import api_client as api

st.set_page_config(page_title="单位管理", page_icon="🏢", layout="wide")

PAGE_SIZE = 10


def _render_login() -> None:
    """登录表单：成功后把令牌放进 session_state，再重跑页面。"""
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


if "access_token" not in st.session_state:
    _render_login()
    st.stop()

user = st.session_state.get("current_user", {})

with st.sidebar:
    st.caption(f"当前用户：{user.get('username', '-')}")
    st.caption(f"角色：{user.get('role', '-')}")
    try:
        status = api.get("/health")
        st.success(f"后端正常：{status.get('status', 'ok')}")
    except api.ApiError as exc:
        st.error(exc.detail)
    if st.button("退出登录", width="stretch", key="logout"):
        st.session_state.clear()
        st.rerun()

st.title("🏢 单位管理")
st.caption("数据来自 GET /departments；新增走 POST /departments。")

# 新增成功后先写提示再重跑；重跑后在这里显示，避免提示被 rerun 冲掉
flash = st.session_state.pop("flash_message", None)
if flash:
    st.success(flash)

# 搜索条件作为查询参数传给后端：params 是请求四要素之一
keyword = st.text_input(
    "按单位名称搜索",
    placeholder="输入名称片段，例如 一中队",
    key="keyword",
)
params = {"page": 1, "page_size": PAGE_SIZE}
if keyword.strip():
    params["full_name"] = keyword.strip()

# 加载态与错误态：请求期间显示 spinner，失败时提示并停止渲染
try:
    with st.spinner("正在加载单位列表..."):
        data = api.get("/departments", params=params)
except api.ApiError as exc:
    if exc.status_code == 401:
        # 令牌过期：清除登录态，重跑后回到登录页并提示
        st.session_state["login_notice"] = exc.detail
        st.rerun()
    st.error(exc.detail)
    st.stop()

items = data.get("items", [])
total = data.get("total", 0)

metric_total, metric_page = st.columns(2)
metric_total.metric("单位数（当前条件）", total)
metric_page.metric("本页显示", len(items))

tab_list, tab_create = st.tabs(["📋 单位列表", "➕ 新增单位"])

with tab_list:
    if not items:
        # 空态：请求成功但没有数据，用 info 而不是 error
        st.info("没有符合条件的单位。可清空搜索，或在「新增单位」页签添加。")
    else:
        table = pd.DataFrame(items)[["dept_code", "full_name", "address"]]
        st.dataframe(
            table,
            width="stretch",
            hide_index=True,
            column_config={
                "dept_code": st.column_config.TextColumn("单位编码", width="small"),
                "full_name": st.column_config.TextColumn("单位名称"),
                "address": st.column_config.TextColumn("地址", width="large"),
            },
        )
        st.caption(f"当前条件下共 {total} 条，显示第 1 页（每页 {PAGE_SIZE} 条）。")

with tab_create:
    st.caption("带 * 的为必填项。单位编码创建后不可修改。")
    with st.form("create_department", clear_on_submit=True):
        dept_code = st.text_input(
            "单位编码 *", placeholder="例如 D003", key="new_dept_code"
        )
        full_name = st.text_input("单位名称 *", key="new_full_name")
        address = st.text_input("地址", key="new_address")
        submitted = st.form_submit_button("提交", type="primary", key="submit_dept")

    if submitted:
        code = dept_code.strip()
        name = full_name.strip()
        if not code or not name:
            st.error("单位编码和单位名称不能为空")
        else:
            try:
                api.post(
                    "/departments",
                    json={
                        "dept_code": code,
                        "full_name": name,
                        "address": address.strip() or None,
                    },
                )
            except api.ApiError as exc:
                # 400 重复编码、401 过期、422 字段校验都在这里统一提示
                if exc.status_code == 401:
                    st.session_state["login_notice"] = exc.detail
                    st.rerun()
                st.error(exc.detail)
            else:
                st.session_state["flash_message"] = f"已新增单位 {code} - {name}"
                st.rerun()
