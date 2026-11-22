"""实训 19-1 人员管理页：筛选、分页、新增、编辑与删除。

写操作三步与单位页一致：
- 新增：校验必填 → POST → 回第 1 页并刷新；
- 编辑：回填当前行 → PUT → 保留当前页与筛选；
- 删除：二次确认 → DELETE → 当前页为空时页码回退。

`certificate_number` 是主键，编辑时禁用输入框；要换证件号只能删除后重建。
"""

import streamlit as st

import api_client as api
import auth
from components.feedback import set_flash, show_flash
from components.table import pagination_bar, render_table
from config import DEFAULT_PAGE_SIZE

st.set_page_config(page_title="人员管理", page_icon="👤", layout="wide")

auth.require_login()
auth.render_user_box()

st.title("👤 人员管理")
st.caption("维护人员信息：按姓名与所属单位筛选，支持新增、编辑与删除。")
show_flash()

# ---------- 单位下拉：新增与筛选共用 ----------
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

# ---------- 状态初始化 ----------
if "person_page" not in st.session_state:
    st.session_state["person_page"] = 1
if "person_page_size" not in st.session_state:
    st.session_state["person_page_size"] = DEFAULT_PAGE_SIZE
if "person_name" not in st.session_state:
    st.session_state["person_name"] = ""
if "person_dept" not in st.session_state:
    st.session_state["person_dept"] = "全部"

# ---------- 筛选区 ----------
with st.container(border=True):
    col_name, col_dept, col_size = st.columns([2, 2, 1])
    with col_name:
        keyword = st.text_input("姓名", placeholder="输入姓名片段", key="person_name")
    with col_dept:
        dept_label = st.selectbox(
            "所属单位", ["全部"] + list(dept_options.keys()), key="person_dept"
        )
    with col_size:
        page_size = st.selectbox(
            "每页条数", [5, DEFAULT_PAGE_SIZE, 20], key="person_page_size"
        )

signature = f"{keyword.strip()}|{dept_label}|{page_size}"
if st.session_state.get("person_query_signature") != signature:
    st.session_state["person_query_signature"] = signature
    st.session_state["person_page"] = 1

page = st.session_state["person_page"]

params = {"page": page, "page_size": page_size}
if keyword.strip():
    params["name"] = keyword.strip()
if dept_label != "全部":
    params["dept_code"] = dept_options[dept_label]

try:
    with st.spinner("正在加载人员列表..."):
        data = api.get("/personnel", params=params)
except api.ApiError as exc:
    if exc.status_code == 401:
        st.session_state["login_notice"] = exc.detail
        st.rerun()
    st.error(exc.detail)
    st.stop()

items = data.get("items", [])
total = data.get("total", 0)

if not items and page > 1:
    st.session_state["person_page"] = page - 1
    st.rerun()

# ---------- 内容区 ----------
st.subheader("人员列表")
metric_total, metric_page = st.columns(2)
metric_total.metric("人员数（当前条件）", total)
metric_page.metric("本页显示", len(items))

if not items:
    st.info("没有符合条件的人员。可清空筛选，或在下方「新增人员」补充。")
else:
    render_table(
        items,
        columns=["certificate_number", "name", "dept_code", "rank"],
        column_config={
            "certificate_number": st.column_config.TextColumn(
                "证件号", width="small"
            ),
            "name": st.column_config.TextColumn("姓名"),
            "dept_code": st.column_config.TextColumn("单位编码", width="small"),
            "rank": st.column_config.TextColumn("职务"),
        },
    )
    new_page = pagination_bar(total, page, page_size, "person")
    if new_page != page:
        st.session_state["person_page"] = new_page
        st.rerun()

# ---------- 操作区：新增 ----------
st.subheader("新增人员")
with st.container(border=True):
    if not dept_options:
        st.info("请先在「单位管理」中新增单位。")
    else:
        st.caption("带 * 的为必填项；证件号创建后不可修改。")
        with st.form("create_personnel", clear_on_submit=True):
            new_cert = st.text_input(
                "证件号 *", placeholder="例如 P003", key="new_person_cert"
            )
            new_name = st.text_input("姓名 *", key="new_person_name")
            new_dept = st.selectbox(
                "所属单位 *", list(dept_options.keys()), key="new_person_dept"
            )
            new_rank = st.text_input("职务", key="new_person_rank")
            submitted = st.form_submit_button(
                "提交", type="primary", key="create_person_submit"
            )

        if submitted:
            cert = new_cert.strip()
            name = new_name.strip()
            if not cert or not name:
                st.error("证件号和姓名不能为空")
            else:
                try:
                    api.post(
                        "/personnel",
                        json={
                            "certificate_number": cert,
                            "name": name,
                            "dept_code": dept_options[new_dept],
                            "rank": new_rank.strip() or None,
                        },
                    )
                except api.ApiError as exc:
                    if exc.status_code == 401:
                        st.session_state["login_notice"] = exc.detail
                        st.rerun()
                    st.error(exc.detail)
                else:
                    st.session_state["person_page"] = 1
                    set_flash(f"已新增人员 {cert} - {name}")
                    st.rerun()

# ---------- 操作区：编辑 ----------
st.subheader("编辑人员")
with st.container(border=True):
    if not items:
        st.info("当前页没有可编辑的人员。")
    else:
        edit_options = {
            f"{p['certificate_number']} - {p['name']}": p for p in items
        }
        edit_label = st.selectbox(
            "选择人员", list(edit_options.keys()), key="person_edit_select"
        )
        selected = edit_options[edit_label]
        cert = selected["certificate_number"]
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

        with st.form(f"edit_personnel_{cert}"):
            st.text_input("证件号（不可修改）", value=cert, disabled=True)
            edit_name = st.text_input(
                "姓名 *", value=selected.get("name", ""), key=f"edit_person_name_{cert}"
            )
            edit_dept = st.selectbox(
                "所属单位 *",
                dept_labels,
                index=dept_index,
                key=f"edit_person_dept_{cert}",
            )
            edit_rank = st.text_input(
                "职务", value=selected.get("rank") or "", key=f"edit_person_rank_{cert}"
            )
            save = st.form_submit_button(
                "保存修改", type="primary", key="person_save"
            )

        if save:
            if not edit_name.strip():
                st.error("姓名不能为空")
            else:
                try:
                    api.put(
                        f"/personnel/{cert}",
                        json={
                            "certificate_number": cert,
                            "name": edit_name.strip(),
                            "dept_code": dept_options[edit_dept],
                            "rank": edit_rank.strip() or None,
                        },
                    )
                except api.ApiError as exc:
                    if exc.status_code == 401:
                        st.session_state["login_notice"] = exc.detail
                        st.rerun()
                    st.error(exc.detail)
                else:
                    set_flash(f"已保存人员 {cert}")
                    st.rerun()

# ---------- 操作区：删除 ----------
st.subheader("删除人员")
with st.container(border=True):
    if not items:
        st.info("当前页没有可删除的人员。")
    else:
        delete_options = {
            f"{p['certificate_number']} - {p['name']}": p for p in items
        }
        delete_label = st.selectbox(
            "选择人员", list(delete_options.keys()), key="person_delete_select"
        )
        target = delete_options[delete_label]
        target_cert = target["certificate_number"]

        st.caption("删除不可撤销；本后端不做级联删除，请先确认该人员没有执勤记录。")
        with st.expander("删除人员（危险操作）"):
            st.caption(f"将删除：{target_cert} - {target['name']}")
            confirm = st.checkbox(
                "我确认要删除该人员", key=f"person_delete_confirm_{target_cert}"
            )
            if st.button(
                "删除", type="primary", disabled=not confirm, key="person_delete"
            ):
                try:
                    api.delete(f"/personnel/{target_cert}")
                except api.ApiError as exc:
                    if exc.status_code == 401:
                        st.session_state["login_notice"] = exc.detail
                        st.rerun()
                    st.error(exc.detail)
                else:
                    set_flash(f"已删除人员 {target_cert}")
                    st.rerun()
