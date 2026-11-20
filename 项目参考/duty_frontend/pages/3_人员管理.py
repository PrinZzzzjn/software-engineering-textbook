"""人员管理页：按单位筛选的列表 / 分页 / 新增 / 编辑 / 删除。

接口（对接 duty-simplified）：
- 列表：GET /personnel?page=&page_size=&dept_code=
- 新增：POST /personnel
- 编辑：PUT /personnel/{certificate_number}
- 删除：DELETE /personnel/{certificate_number}

字段：certificate_number（主键）/ name / dept_code（外键）/ rank（职级）。
dept_code 是后端支持的服务端筛选参数；所属单位必须已存在，否则后端返回 400。
"""

import streamlit as st

import api_client as api
import auth
import ui
from components.table import pagination_bar, render_table

st.set_page_config(page_title="人员管理", page_icon="👤", layout="wide")
ui.inject_css()
auth.require_login()
auth.render_user_box()
ui.show_flash()

ui.page_header(
    "人员管理",
    "维护执勤人员：按单位筛选、分页浏览，录入与修改证件号、姓名、职级。",
    "👤",
)

# 单位下拉选项（用于筛选与新增表单）
try:
    dept_data = api.get("/departments", params={"page": 1, "page_size": 100})
    dept_options = [d["dept_code"] for d in dept_data.get("items", [])]
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

# 分页与筛选状态放在 session_state
for key, default in [
    ("personnel_page", 1),
    ("personnel_dept_filter", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        dept_filter = st.selectbox(
            "按单位筛选",
            options=[""] + dept_options,
            format_func=lambda x: "全部单位" if x == "" else x,
            key="personnel_dept_filter",
        )
    with col2:
        st.caption(f"每页 {st.session_state.get('personnel_page_size', 10)} 条")

params = {
    "page": st.session_state.personnel_page,
    "page_size": 10,
}
if dept_filter:
    params["dept_code"] = dept_filter

try:
    with st.spinner("正在加载人员列表..."):
        data = api.get("/personnel", params=params)
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

items = data.get("items", [])

tab_list, tab_create, tab_edit = st.tabs(
    ["📋 人员列表", "➕ 新增人员", "✏️ 编辑 / 删除"]
)

# ----------------------------- 列表 ---------------------------------------
with tab_list:
    if items:
        column_config = {
            "certificate_number": st.column_config.TextColumn("证件号", width="small"),
            "name": st.column_config.TextColumn("姓名"),
            "dept_code": st.column_config.TextColumn("单位编码", width="small"),
            "rank": st.column_config.TextColumn("职级"),
        }
        render_table(
            items,
            columns=["certificate_number", "name", "dept_code", "rank"],
            column_config=column_config,
        )
    else:
        st.info("没有符合条件的人员")

    new_page = pagination_bar(
        data.get("total", 0),
        st.session_state.personnel_page,
        10,
        "personnel",
    )
    if new_page != st.session_state.personnel_page:
        st.session_state.personnel_page = new_page
        st.rerun()

# ----------------------------- 新增 ---------------------------------------
with tab_create:
    st.caption("带 * 的为必填项。证件号创建后不可修改；所属单位须先存在。")
    with st.form("create_personnel", clear_on_submit=True):
        certificate_number = st.text_input("证件号 *", placeholder="例如 P003")
        name = st.text_input("姓名 *")
        dept_code = st.selectbox(
            "所属单位 *",
            options=dept_options,
            disabled=not dept_options,
        )
        rank = st.text_input("职级（可空）")
        submitted = st.form_submit_button("提交", type="primary")

    if submitted:
        if not certificate_number.strip() or not name.strip():
            st.error("证件号和姓名不能为空")
        elif not dept_code:
            st.error("请先录入单位，再新增人员")
        else:
            try:
                api.post(
                    "/personnel",
                    json={
                        "certificate_number": certificate_number.strip(),
                        "name": name.strip(),
                        "dept_code": dept_code,
                        "rank": rank or None,
                    },
                )
                ui.set_flash("人员新增成功")
                st.rerun()
            except api.ApiError as exc:
                st.error(exc.detail)

# ----------------------------- 编辑 / 删除 --------------------------------
with tab_edit:
    if not items:
        st.info("当前页没有可编辑的人员")
    else:
        options = {
            f"{p['name']}（{p['certificate_number']}）": p for p in items
        }
        selected_label = st.selectbox("选择人员", list(options.keys()))
        selected = options[selected_label]
        key_suffix = selected["certificate_number"]

        with st.form("edit_personnel"):
            st.text_input(
                "证件号",
                value=selected["certificate_number"],
                disabled=True,
                key=f"edit_cert_{key_suffix}",
            )
            name = st.text_input(
                "姓名",
                value=selected.get("name", ""),
                key=f"edit_name_{key_suffix}",
            )
            current_dept = selected["dept_code"]
            dept_index = dept_options.index(current_dept) if current_dept in dept_options else 0
            dept_code = st.selectbox(
                "所属单位",
                options=dept_options,
                index=dept_index,
                disabled=not dept_options,
                key=f"edit_dept_{key_suffix}",
            )
            rank = st.text_input(
                "职级",
                value=selected.get("rank") or "",
                key=f"edit_rank_{key_suffix}",
            )
            save = st.form_submit_button("保存修改", type="primary")

        if save:
            try:
                api.put(
                    f"/personnel/{selected['certificate_number']}",
                    json={
                        "certificate_number": selected["certificate_number"],
                        "name": name,
                        "dept_code": dept_code,
                        "rank": rank or None,
                    },
                )
                ui.set_flash("人员修改成功")
                st.rerun()
            except api.ApiError as exc:
                st.error(exc.detail)

        st.divider()
        with st.expander("删除人员（危险操作）"):
            st.caption(f"将删除：{selected['name']}（{selected['certificate_number']}）")
            confirm = st.checkbox(
                "我确认要删除该人员",
                key=f"personnel_delete_confirm_{key_suffix}",
            )
            if st.button("删除", type="primary", disabled=not confirm):
                try:
                    api.delete(f"/personnel/{selected['certificate_number']}")
                    ui.set_flash("人员删除成功")
                    st.rerun()
                except api.ApiError as exc:
                    st.error(exc.detail)
