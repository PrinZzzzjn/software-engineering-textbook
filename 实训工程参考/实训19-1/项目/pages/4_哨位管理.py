"""实训 19-1 哨位管理页：筛选、分页、新增、编辑与删除。

`workstation_id` 是主键，编辑时禁用；`is_active` 用复选框映射为 0/1。
写操作三步与单位页、人员页一致，成功统一 `st.rerun()` 重新取数。
"""

import streamlit as st

import api_client as api
import auth
from components.feedback import set_flash, show_flash
from components.table import pagination_bar, render_table
from config import DEFAULT_PAGE_SIZE

st.set_page_config(page_title="哨位管理", page_icon="🛡️", layout="wide")

auth.require_login()
auth.render_user_box()

st.title("🛡️ 哨位管理")
st.caption("维护哨位信息：按所属单位筛选，支持新增、编辑与删除。")
show_flash()

try:
    departments = api.get(
        "/departments", params={"page": 1, "page_size": 100}
    ).get("items", [])
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

dept_options = {
    f"{d['dept_code']} - {d['full_name']}": d["dept_code"] for d in departments
}

if "station_page" not in st.session_state:
    st.session_state["station_page"] = 1
if "station_page_size" not in st.session_state:
    st.session_state["station_page_size"] = DEFAULT_PAGE_SIZE
if "station_dept" not in st.session_state:
    st.session_state["station_dept"] = "全部"

# ---------- 筛选区 ----------
with st.container(border=True):
    col_dept, col_size = st.columns([3, 1])
    with col_dept:
        dept_label = st.selectbox(
            "所属单位", ["全部"] + list(dept_options.keys()), key="station_dept"
        )
    with col_size:
        page_size = st.selectbox(
            "每页条数", [5, DEFAULT_PAGE_SIZE, 20], key="station_page_size"
        )

signature = f"{dept_label}|{page_size}"
if st.session_state.get("station_query_signature") != signature:
    st.session_state["station_query_signature"] = signature
    st.session_state["station_page"] = 1

page = st.session_state["station_page"]

params = {"page": page, "page_size": page_size}
if dept_label != "全部":
    params["dept_code"] = dept_options[dept_label]

try:
    with st.spinner("正在加载哨位列表..."):
        data = api.get("/workstations", params=params)
except api.ApiError as exc:
    if exc.status_code == 401:
        st.session_state["login_notice"] = exc.detail
        st.rerun()
    st.error(exc.detail)
    st.stop()

items = data.get("items", [])
total = data.get("total", 0)

if not items and page > 1:
    st.session_state["station_page"] = page - 1
    st.rerun()

# ---------- 内容区 ----------
st.subheader("哨位列表")
metric_total, metric_page = st.columns(2)
metric_total.metric("哨位数（当前条件）", total)
metric_page.metric("本页显示", len(items))

if not items:
    st.info("没有符合条件的哨位。可清空筛选，或在下方「新增哨位」补充。")
else:
    render_table(
        items,
        columns=["workstation_id", "name", "dept_code", "is_active"],
        column_config={
            "workstation_id": st.column_config.TextColumn(
                "哨位编号", width="small"
            ),
            "name": st.column_config.TextColumn("哨位名称"),
            "dept_code": st.column_config.TextColumn("单位编码", width="small"),
            "is_active": st.column_config.NumberColumn("启用（1/0）", width="small"),
        },
    )
    new_page = pagination_bar(total, page, page_size, "station")
    if new_page != page:
        st.session_state["station_page"] = new_page
        st.rerun()

# ---------- 操作区：新增 ----------
st.subheader("新增哨位")
with st.container(border=True):
    if not dept_options:
        st.info("请先在「单位管理」中新增单位。")
    else:
        st.caption("带 * 的为必填项；哨位编号创建后不可修改。")
        with st.form("create_workstation", clear_on_submit=True):
            new_id = st.text_input(
                "哨位编号 *", placeholder="例如 W003", key="new_station_id"
            )
            new_name = st.text_input("哨位名称 *", key="new_station_name")
            new_dept = st.selectbox(
                "所属单位 *", list(dept_options.keys()), key="new_station_dept"
            )
            new_active = st.checkbox("启用", value=True, key="new_station_active")
            submitted = st.form_submit_button(
                "提交", type="primary", key="create_station_submit"
            )

        if submitted:
            station_id = new_id.strip()
            name = new_name.strip()
            if not station_id or not name:
                st.error("哨位编号和哨位名称不能为空")
            else:
                try:
                    api.post(
                        "/workstations",
                        json={
                            "workstation_id": station_id,
                            "name": name,
                            "dept_code": dept_options[new_dept],
                            "is_active": 1 if new_active else 0,
                        },
                    )
                except api.ApiError as exc:
                    if exc.status_code == 401:
                        st.session_state["login_notice"] = exc.detail
                        st.rerun()
                    st.error(exc.detail)
                else:
                    st.session_state["station_page"] = 1
                    set_flash(f"已新增哨位 {station_id} - {name}")
                    st.rerun()

# ---------- 操作区：编辑 ----------
st.subheader("编辑哨位")
with st.container(border=True):
    if not items:
        st.info("当前页没有可编辑的哨位。")
    else:
        edit_options = {
            f"{w['workstation_id']} - {w['name']}": w for w in items
        }
        edit_label = st.selectbox(
            "选择哨位", list(edit_options.keys()), key="station_edit_select"
        )
        selected = edit_options[edit_label]
        station_id = selected["workstation_id"]
        current_dept = next(
            (
                label
                for label, code in dept_options.items()
                if code == selected["dept_code"]
            ),
            None,
        )
        dept_labels = list(dept_options.keys())
        dept_index = dept_labels.index(current_dept) if current_dept else 0

        with st.form(f"edit_workstation_{station_id}"):
            st.text_input("哨位编号（不可修改）", value=station_id, disabled=True)
            edit_name = st.text_input(
                "哨位名称 *",
                value=selected.get("name", ""),
                key=f"edit_station_name_{station_id}",
            )
            edit_dept = st.selectbox(
                "所属单位 *",
                dept_labels,
                index=dept_index,
                key=f"edit_station_dept_{station_id}",
            )
            edit_active = st.checkbox(
                "启用",
                value=bool(selected.get("is_active")),
                key=f"edit_station_active_{station_id}",
            )
            save = st.form_submit_button(
                "保存修改", type="primary", key="station_save"
            )

        if save:
            if not edit_name.strip():
                st.error("哨位名称不能为空")
            else:
                try:
                    api.put(
                        f"/workstations/{station_id}",
                        json={
                            "workstation_id": station_id,
                            "name": edit_name.strip(),
                            "dept_code": dept_options[edit_dept],
                            "is_active": 1 if edit_active else 0,
                        },
                    )
                except api.ApiError as exc:
                    if exc.status_code == 401:
                        st.session_state["login_notice"] = exc.detail
                        st.rerun()
                    st.error(exc.detail)
                else:
                    set_flash(f"已保存哨位 {station_id}")
                    st.rerun()

# ---------- 操作区：删除 ----------
st.subheader("删除哨位")
with st.container(border=True):
    if not items:
        st.info("当前页没有可删除的哨位。")
    else:
        delete_options = {
            f"{w['workstation_id']} - {w['name']}": w for w in items
        }
        delete_label = st.selectbox(
            "选择哨位", list(delete_options.keys()), key="station_delete_select"
        )
        target = delete_options[delete_label]
        target_id = target["workstation_id"]

        st.caption("删除不可撤销；本后端不做级联删除，请先确认该哨位没有执勤记录。")
        with st.expander("删除哨位（危险操作）"):
            st.caption(f"将删除：{target_id} - {target['name']}")
            confirm = st.checkbox(
                "我确认要删除该哨位", key=f"station_delete_confirm_{target_id}"
            )
            if st.button(
                "删除", type="primary", disabled=not confirm, key="station_delete"
            ):
                try:
                    api.delete(f"/workstations/{target_id}")
                except api.ApiError as exc:
                    if exc.status_code == 401:
                        st.session_state["login_notice"] = exc.detail
                        st.rerun()
                    st.error(exc.detail)
                else:
                    set_flash(f"已删除哨位 {target_id}")
                    st.rerun()
