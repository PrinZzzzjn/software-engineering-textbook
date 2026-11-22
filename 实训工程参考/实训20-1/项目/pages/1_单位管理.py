"""实训 20-1 单位管理页：列表、搜索、分页、新增、编辑与删除。

本页在原 17-1 四区结构上补齐写操作三步（校验—提交—刷新）：
- 新增：表单校验 → POST → 清空表单并回到第 1 页；
- 编辑：按对象回填 → PUT → 保留当前页与筛选；
- 删除：二次确认 → DELETE → 当前页为空时页码回退一页。

页面状态归属：
- 数据由后端决定，成功后统一 `st.rerun()` 重新取数，不手动改列表；
- 页码、每页条数、搜索词放 `session_state`；
- 编辑表单的 `key` 带对象标识，切换单位时输入框重新取值；
- 操作反馈先存 `_flash`，重跑后由 `show_flash()` 显示一次。
"""

import streamlit as st

import api_client as api
import auth
from components.errors import show_api_error
from components.feedback import set_flash, show_flash
from components.table import pagination_bar, render_table
from config import DEFAULT_PAGE_SIZE

st.set_page_config(page_title="单位管理", page_icon="🏢", layout="wide")

# 访问守卫：写在页面最上面，未登录时不会再发列表请求
auth.require_login()
auth.render_user_box()

# ---------- 标题区 ----------
st.title("🏢 单位管理")
st.caption("维护执勤业务中的单位信息：查询、分页、新增、编辑与删除。")

# 操作反馈：上一次写操作留下的消息，在本次渲染显示一次后清除
show_flash()

# ---------- 状态初始化：只做一次，避免每次重跑把页码覆盖回 1 ----------
if "dept_page" not in st.session_state:
    st.session_state["dept_page"] = 1
if "dept_page_size" not in st.session_state:
    st.session_state["dept_page_size"] = DEFAULT_PAGE_SIZE
if "dept_keyword" not in st.session_state:
    st.session_state["dept_keyword"] = ""

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
            key="dept_page_size",
        )

# 搜索词或每页条数变化时回到第 1 页，避免停在不存在的页码
signature = f"{keyword.strip()}|{page_size}"
if st.session_state.get("dept_query_signature") != signature:
    st.session_state["dept_query_signature"] = signature
    st.session_state["dept_page"] = 1

page = st.session_state["dept_page"]

# 取数永远放在操作之前：写操作成功后重跑，这里会重新向接口要最新数据
params = {"page": page, "page_size": page_size}
if keyword.strip():
    params["full_name"] = keyword.strip()

try:
    with st.spinner("正在加载单位列表..."):
        data = api.get("/departments", params=params)
except api.ApiError as exc:
    # 状态码 → 提示的统一映射在 components/errors.py；401 会清会话并回登录页
    show_api_error(exc)
    st.stop()

items = data.get("items", [])
total = data.get("total", 0)

# 删除当前页最后一条后，页码回退一页（教材 18.4）
if not items and page > 1:
    st.session_state["dept_page"] = page - 1
    st.rerun()

# ---------- 内容区 ----------
st.subheader("单位列表")
metric_total, metric_page = st.columns(2)
metric_total.metric("单位数（当前条件）", total)
metric_page.metric("本页显示", len(items))

if not items:
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

# ---------- 操作区：新增 ----------
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
            # 400 显示后端 detail；422 由统一组件加「提交内容有误」前缀
            show_api_error(exc)
        else:
            # 回到第 1 页，保证新增记录在排序后的首页可见
            st.session_state["dept_page"] = 1
            set_flash(f"已新增单位 {code} - {name}")
            st.rerun()

# ---------- 操作区：编辑 ----------
st.subheader("编辑单位")
with st.container(border=True):
    if not items:
        st.info("当前页没有可编辑的单位。")
    else:
        edit_options = {
            f"{d['dept_code']} - {d['full_name']}": d for d in items
        }
        edit_label = st.selectbox(
            "选择单位", list(edit_options.keys()), key="dept_edit_select"
        )
        selected = edit_options[edit_label]
        selected_code = selected["dept_code"]

        # key 带上单位编码：切换单位相当于新建组件，value 重新生效
        with st.form(f"edit_department_{selected_code}"):
            st.text_input(
                "单位编码（不可修改）", value=selected_code, disabled=True
            )
            edit_name = st.text_input(
                "单位名称 *",
                value=selected.get("full_name", ""),
                key=f"edit_dept_name_{selected_code}",
            )
            edit_address = st.text_input(
                "地址",
                value=selected.get("address") or "",
                key=f"edit_dept_address_{selected_code}",
            )
            save = st.form_submit_button(
                "保存修改", type="primary", key="dept_save"
            )

        if save:
            if not edit_name.strip():
                st.error("单位名称不能为空")
            else:
                try:
                    api.put(
                        f"/departments/{selected_code}",
                        json={
                            "dept_code": selected_code,
                            "full_name": edit_name.strip(),
                            "address": edit_address.strip() or None,
                        },
                    )
                except api.ApiError as exc:
                    show_api_error(exc)
                else:
                    # 不清页码：编辑后仍停在原来的页与原筛选条件
                    set_flash(f"已保存单位 {selected_code}")
                    st.rerun()

# ---------- 操作区：删除 ----------
st.subheader("删除单位")
with st.container(border=True):
    if not items:
        st.info("当前页没有可删除的单位。")
    else:
        delete_options = {
            f"{d['dept_code']} - {d['full_name']}": d for d in items
        }
        delete_label = st.selectbox(
            "选择单位", list(delete_options.keys()), key="dept_delete_select"
        )
        target = delete_options[delete_label]
        target_code = target["dept_code"]

        st.caption("删除不可撤销；本后端不做级联删除，请先确认该单位下没有人员与哨位。")
        with st.expander("删除单位（危险操作）"):
            st.caption(f"将删除：{target_code} - {target['full_name']}")
            confirm = st.checkbox(
                "我确认要删除该单位", key=f"dept_delete_confirm_{target_code}"
            )
            if st.button(
                "删除", type="primary", disabled=not confirm, key="dept_delete"
            ):
                try:
                    api.delete(f"/departments/{target_code}")
                except api.ApiError as exc:
                    show_api_error(exc)
                else:
                    set_flash(f"已删除单位 {target_code}")
                    st.rerun()
