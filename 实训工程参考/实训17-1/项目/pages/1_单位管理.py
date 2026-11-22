"""实训 17-1 单位管理页：列表、搜索、分页与新增。

页面按四个区域组织：标题 → 筛选 → 内容 → 操作。
每个子页面都是独立脚本，顶部必须先调用 auth.require_login()；
编辑与删除留到 18-1。
"""

import streamlit as st

import api_client as api
import auth
from components.table import pagination_bar, render_table
from config import DEFAULT_PAGE_SIZE

st.set_page_config(page_title="单位管理", page_icon="🏢", layout="wide")

# 访问守卫：写在页面最上面，未登录时不会再发列表请求
auth.require_login()
auth.render_user_box()

# ---------- 标题区 ----------
st.title("🏢 单位管理")
st.caption("维护执勤业务中的单位信息：查询、分页与新增。")

# ---------- 筛选区 ----------
with st.container(border=True):
    col_keyword, col_size = st.columns([3, 1])
    with col_keyword:
        keyword = st.text_input(
            "单位名称",
            placeholder="输入名称片段，例如 一中队",
            key="dept_keyword",
        )
    with col_size:
        page_size = st.selectbox(
            "每页条数",
            [5, DEFAULT_PAGE_SIZE, 20],
            index=1,
            key="dept_page_size",
        )

# 搜索词或每页条数变化时回到第 1 页，避免停在不存在的页码
signature = f"{keyword.strip()}|{page_size}"
if st.session_state.get("dept_query_signature") != signature:
    st.session_state["dept_query_signature"] = signature
    st.session_state["dept_page"] = 1
page = st.session_state.get("dept_page", 1)

# 新增成功后先写提示再重跑；重跑后在这里显示，避免提示被 rerun 冲掉
flash = st.session_state.pop("flash_message", None)
if flash:
    st.success(flash)

params = {"page": page, "page_size": page_size}
if keyword.strip():
    params["full_name"] = keyword.strip()

try:
    with st.spinner("正在加载单位列表..."):
        data = api.get("/departments", params=params)
except api.ApiError as exc:
    if exc.status_code == 401:
        st.session_state["login_notice"] = exc.detail
        st.rerun()
    st.error(exc.detail)
    st.stop()

items = data.get("items", [])
total = data.get("total", 0)

# ---------- 内容区 ----------
st.subheader("单位列表")
metric_total, metric_page = st.columns(2)
metric_total.metric("单位数（当前条件）", total)
metric_page.metric("本页显示", len(items))

if not items:
    # 空态：请求成功但没有数据，用 info 而不是 error
    st.info("没有符合条件的单位。可清空搜索，或在下方「新增单位」补充。")
else:
    render_table(
        items,
        columns=["dept_code", "full_name", "address"],
        column_config={
            "dept_code": st.column_config.TextColumn("单位编码", width="small"),
            "full_name": st.column_config.TextColumn("单位名称"),
            "address": st.column_config.TextColumn("地址", width="large"),
        },
    )
    new_page = pagination_bar(total, page, page_size, "dept")
    if new_page != page:
        st.session_state["dept_page"] = new_page
        st.rerun()

# ---------- 操作区 ----------
st.subheader("新增单位")
with st.container(border=True):
    st.caption("带 * 的为必填项；单位编码创建后不可修改。")
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
