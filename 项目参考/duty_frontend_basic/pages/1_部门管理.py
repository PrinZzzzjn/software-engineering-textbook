"""单位管理页：列表 / 分页 / 新增 / 编辑 / 删除。

这一页是"通用 CRUD 样板"（对应第 15、17、18 章）：
- 列表：GET /departments?page=&page_size=
- 新增：POST /departments
- 编辑：PUT /departments/{dept_code}
- 删除：DELETE /departments/{dept_code}

字段只有 dept_code / full_name / address 三个，列表只返回 items 与 total；
后端排序固定，前端不传 sort_by / order 之类的参数。
集合路径无尾斜杠。
"""

import streamlit as st

import api_client as api
import auth
from components.table import pagination_bar, render_table

st.set_page_config(page_title="单位管理", page_icon="🏢", layout="wide")
auth.require_login()
auth.render_user_box()

st.title("🏢 单位管理")
st.caption("维护执勤业务中的单位信息：查询、分页、新增、编辑与删除。")


# 分页状态放在 session_state 里，翻页后仍然保留
if "dept_page" not in st.session_state:
    st.session_state.dept_page = 1
if "dept_page_size" not in st.session_state:
    st.session_state.dept_page_size = 10

params = {
    "page": st.session_state.dept_page,
    "page_size": st.session_state.dept_page_size,
}

try:
    with st.spinner("正在加载单位列表..."):
        data = api.get("/departments", params=params)
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

items = data.get("items", [])

# 三个分区：列表 / 新增 / 编辑删除
tab_list, tab_create, tab_edit = st.tabs(
    ["📋 单位列表", "➕ 新增单位", "✏️ 编辑 / 删除"]
)

# ----------------------------- 列表 ---------------------------------------
with tab_list:
    if items:
        column_config = {
            "dept_code": st.column_config.TextColumn("单位编码", width="small"),
            "full_name": st.column_config.TextColumn("单位名称"),
            "address": st.column_config.TextColumn("地址"),
        }
        render_table(
            items,
            columns=["dept_code", "full_name", "address"],
            column_config=column_config,
        )
    else:
        st.info("没有单位数据")

    new_page = pagination_bar(
        data.get("total", 0),
        st.session_state.dept_page,
        st.session_state.dept_page_size,
        "dept",
    )
    if new_page != st.session_state.dept_page:
        st.session_state.dept_page = new_page
        st.rerun()

# ----------------------------- 新增 ---------------------------------------
with tab_create:
    st.caption("带 * 的为必填项。单位编码创建后不可修改。")
    with st.form("create_department", clear_on_submit=True):
        dept_code = st.text_input("单位编码 *", placeholder="例如 D003")
        full_name = st.text_input("单位名称 *")
        address = st.text_input("地址")
        submitted = st.form_submit_button("提交", type="primary")

    if submitted:
        if not dept_code.strip() or not full_name.strip():
            st.error("单位编码和单位名称不能为空")
        else:
            try:
                api.post(
                    "/departments",
                    json={
                        "dept_code": dept_code.strip(),
                        "full_name": full_name.strip(),
                        "address": address or None,
                    },
                )
                st.success("单位新增成功")
                st.rerun()
            except api.ApiError as exc:
                st.error(exc.detail)

# ----------------------------- 编辑 / 删除 --------------------------------
with tab_edit:
    if not items:
        st.info("当前页没有可编辑的单位")
    else:
        options = {f"{d['dept_code']} - {d['full_name']}": d for d in items}
        selected_label = st.selectbox("选择单位", list(options.keys()))
        selected = options[selected_label]
        key_suffix = selected["dept_code"]

        with st.form("edit_department"):
            st.text_input(
                "单位编码",
                value=selected["dept_code"],
                disabled=True,
                key=f"edit_code_{key_suffix}",
            )
            full_name = st.text_input(
                "单位名称",
                value=selected.get("full_name", ""),
                key=f"edit_full_name_{key_suffix}",
            )
            address = st.text_input(
                "地址",
                value=selected.get("address") or "",
                key=f"edit_address_{key_suffix}",
            )
            save = st.form_submit_button("保存修改", type="primary")

        if save:
            try:
                api.put(
                    f"/departments/{selected['dept_code']}",
                    json={
                        "dept_code": selected["dept_code"],
                        "full_name": full_name,
                        "address": address or None,
                    },
                )
                st.success("单位修改成功")
                st.rerun()
            except api.ApiError as exc:
                st.error(exc.detail)

        st.divider()
        with st.expander("删除单位（危险操作）"):
            st.caption(f"将删除：{selected['dept_code']} - {selected['full_name']}")
            confirm = st.checkbox(
                "我确认要删除该单位",
                key=f"dept_delete_confirm_{selected['dept_code']}",
            )
            if st.button("删除", type="primary", disabled=not confirm):
                try:
                    api.delete(f"/departments/{selected['dept_code']}")
                    st.success("单位删除成功")
                    st.rerun()
                except api.ApiError as exc:
                    st.error(exc.detail)
