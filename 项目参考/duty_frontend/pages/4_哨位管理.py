"""哨位管理页：按单位筛选的列表 / 分页 / 新增 / 编辑 / 删除。

接口（对接 duty-simplified）：
- 列表：GET /workstations?page=&page_size=&dept_code=
- 新增：POST /workstations
- 编辑：PUT /workstations/{workstation_id}
- 删除：DELETE /workstations/{workstation_id}

字段：workstation_id（主键）/ name / dept_code（外键）/ is_active（启用状态，0 或 1）。
所属单位必须已存在，否则后端返回 400。
"""

import streamlit as st

import api_client as api
import auth
import ui
from components.table import pagination_bar, render_table

st.set_page_config(page_title="哨位管理", page_icon="🛡️", layout="wide")
ui.inject_css()
auth.require_login()
auth.render_user_box()
ui.show_flash()

ui.page_header(
    "哨位管理",
    "维护执勤哨位：按单位筛选，设置启用或停用；在已停用哨位上不能新增执勤记录。",
    "🛡️",
)

# 单位下拉选项
try:
    dept_data = api.get("/departments", params={"page": 1, "page_size": 100})
    dept_options = [d["dept_code"] for d in dept_data.get("items", [])]
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

if "workstation_page" not in st.session_state:
    st.session_state.workstation_page = 1
if "workstation_dept_filter" not in st.session_state:
    st.session_state.workstation_dept_filter = ""

with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        dept_filter = st.selectbox(
            "按单位筛选",
            options=[""] + dept_options,
            format_func=lambda x: "全部单位" if x == "" else x,
            key="workstation_dept_filter",
        )
    with col2:
        st.caption("is_active：1 启用 / 0 停用")

params = {"page": st.session_state.workstation_page, "page_size": 10}
if dept_filter:
    params["dept_code"] = dept_filter

try:
    with st.spinner("正在加载哨位列表..."):
        data = api.get("/workstations", params=params)
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

items = data.get("items", [])

tab_list, tab_create, tab_edit = st.tabs(
    ["📋 哨位列表", "➕ 新增哨位", "✏️ 编辑 / 删除"]
)

# ----------------------------- 列表 ---------------------------------------
with tab_list:
    if items:
        column_config = {
            "workstation_id": st.column_config.TextColumn("哨位编号", width="small"),
            "name": st.column_config.TextColumn("哨位名称"),
            "dept_code": st.column_config.TextColumn("单位编码", width="small"),
            "is_active": st.column_config.NumberColumn("启用状态", format="%d"),
        }
        render_table(
            items,
            columns=["workstation_id", "name", "dept_code", "is_active"],
            column_config=column_config,
        )
    else:
        st.info("没有符合条件的哨位")

    new_page = pagination_bar(
        data.get("total", 0),
        st.session_state.workstation_page,
        10,
        "workstation",
    )
    if new_page != st.session_state.workstation_page:
        st.session_state.workstation_page = new_page
        st.rerun()

# ----------------------------- 新增 ---------------------------------------
with tab_create:
    st.caption("带 * 的为必填项。哨位编号创建后不可修改；所属单位须先存在。")
    with st.form("create_workstation", clear_on_submit=True):
        workstation_id = st.text_input("哨位编号 *", placeholder="例如 W003")
        name = st.text_input("哨位名称 *")
        dept_code = st.selectbox(
            "所属单位 *",
            options=dept_options,
            disabled=not dept_options,
        )
        is_active = st.selectbox("启用状态", options=[1, 0], format_func=lambda x: "启用" if x == 1 else "停用")
        submitted = st.form_submit_button("提交", type="primary")

    if submitted:
        if not workstation_id.strip() or not name.strip():
            st.error("哨位编号和哨位名称不能为空")
        elif not dept_code:
            st.error("请先录入单位，再新增哨位")
        else:
            try:
                api.post(
                    "/workstations",
                    json={
                        "workstation_id": workstation_id.strip(),
                        "name": name.strip(),
                        "dept_code": dept_code,
                        "is_active": is_active,
                    },
                )
                ui.set_flash("哨位新增成功")
                st.rerun()
            except api.ApiError as exc:
                st.error(exc.detail)

# ----------------------------- 编辑 / 删除 --------------------------------
with tab_edit:
    if not items:
        st.info("当前页没有可编辑的哨位")
    else:
        options = {f"{w['name']}（{w['workstation_id']}）": w for w in items}
        selected_label = st.selectbox("选择哨位", list(options.keys()))
        selected = options[selected_label]
        key_suffix = selected["workstation_id"]

        with st.form("edit_workstation"):
            st.text_input(
                "哨位编号",
                value=selected["workstation_id"],
                disabled=True,
                key=f"edit_wid_{key_suffix}",
            )
            name = st.text_input(
                "哨位名称",
                value=selected.get("name", ""),
                key=f"edit_wname_{key_suffix}",
            )
            current_dept = selected["dept_code"]
            dept_index = dept_options.index(current_dept) if current_dept in dept_options else 0
            dept_code = st.selectbox(
                "所属单位",
                options=dept_options,
                index=dept_index,
                disabled=not dept_options,
                key=f"edit_wdept_{key_suffix}",
            )
            current_active = int(selected.get("is_active", 1))
            is_active = st.selectbox(
                "启用状态",
                options=[1, 0],
                index=0 if current_active == 1 else 1,
                format_func=lambda x: "启用" if x == 1 else "停用",
                key=f"edit_wactive_{key_suffix}",
            )
            save = st.form_submit_button("保存修改", type="primary")

        if save:
            try:
                api.put(
                    f"/workstations/{selected['workstation_id']}",
                    json={
                        "workstation_id": selected["workstation_id"],
                        "name": name,
                        "dept_code": dept_code,
                        "is_active": is_active,
                    },
                )
                ui.set_flash("哨位修改成功")
                st.rerun()
            except api.ApiError as exc:
                st.error(exc.detail)

        st.divider()
        with st.expander("删除哨位（危险操作）"):
            st.caption(f"将删除：{selected['name']}（{selected['workstation_id']}）")
            confirm = st.checkbox(
                "我确认要删除该哨位",
                key=f"workstation_delete_confirm_{key_suffix}",
            )
            if st.button("删除", type="primary", disabled=not confirm):
                try:
                    api.delete(f"/workstations/{selected['workstation_id']}")
                    ui.set_flash("哨位删除成功")
                    st.rerun()
                except api.ApiError as exc:
                    st.error(exc.detail)
