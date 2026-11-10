"""部门管理页：列表 / 搜索 / 分页 / 新增 / 编辑 / 删除。

这一页是"通用 CRUD 样板"（对应课次 17、18、19）：
- 列表：GET /api/v1/departments/
- 新增：POST /api/v1/departments/
- 编辑：PUT /api/v1/departments/{dept_code}
- 删除：DELETE /api/v1/departments/{dept_code}

人员、工位等模块的页面可以照这个结构复制，只改接口路径和字段。
"""

import streamlit as st

import api_client as api
import auth
from components.table import pagination_bar, render_table

st.set_page_config(page_title="部门管理", page_icon="🏢", layout="wide")
auth.require_login()
auth.render_user_box()

st.title("🏢 部门管理")

# ---------------------------------------------------------------------------
# 1. 查询条件
# ---------------------------------------------------------------------------
with st.expander("查询条件", expanded=True):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        keyword = st.text_input("部门名称", placeholder="输入关键字后回车")
    with col2:
        # duty 的部门列表排序字段是 sort_by + sort_order（注意不是 order）
        sort_by = st.selectbox("排序字段", ["create_time", "full_name", "dept_code"])
    with col3:
        sort_order = st.selectbox("排序方式", ["desc", "asc"])

# 分页状态放在 session_state 里，翻页后仍然保留
if "dept_page" not in st.session_state:
    st.session_state.dept_page = 1
if "dept_page_size" not in st.session_state:
    st.session_state.dept_page_size = 10

params = {
    "page": st.session_state.dept_page,
    "page_size": st.session_state.dept_page_size,
    "sort_by": sort_by,
    "sort_order": sort_order,
}
if keyword:
    params["full_name"] = keyword

try:
    with st.spinner("正在加载部门列表..."):
        data = api.get("/departments/", params=params)
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

render_table(
    data.get("items", []),
    columns=["dept_code", "full_name", "address", "parent_dept_code", "created_at"],
)

new_page = pagination_bar(
    data.get("total", 0),
    st.session_state.dept_page,
    st.session_state.dept_page_size,
    "dept",
)
if new_page != st.session_state.dept_page:
    st.session_state.dept_page = new_page
    st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# 2. 新增部门（注意：后端 DepartmentCreate 要求 dept_code 必填）
# ---------------------------------------------------------------------------
with st.expander("新增部门"):
    with st.form("create_dept", clear_on_submit=True):
        dept_code = st.text_input("部门编码 *", placeholder="例如 1001")
        full_name = st.text_input("部门名称 *")
        address = st.text_input("地址")

        col1, col2 = st.columns(2)
        with col1:
            longitude = st.number_input("经度", value=116.397, format="%.3f")
        with col2:
            latitude = st.number_input("纬度", value=39.908, format="%.3f")

        parent_dept_code = st.text_input("父部门编码（可空）")
        submitted = st.form_submit_button("提交")

    if submitted:
        if not dept_code.strip() or not full_name.strip():
            st.error("部门编码和部门名称不能为空")
        else:
            try:
                api.post(
                    "/departments/",
                    json={
                        "dept_code": dept_code.strip(),
                        "full_name": full_name.strip(),
                        "address": address or None,
                        "longitude": longitude,
                        "latitude": latitude,
                        "parent_dept_code": parent_dept_code or None,
                    },
                )
                st.success("新增成功")
                st.rerun()
            except api.ApiError as exc:
                st.error(exc.detail)

# ---------------------------------------------------------------------------
# 3. 编辑 / 删除（针对当前页选中的部门）
# ---------------------------------------------------------------------------
st.subheader("编辑 / 删除")
items = data.get("items", [])

if not items:
    st.info("当前页没有可编辑的部门")
else:
    options = {f"{d['dept_code']} - {d['full_name']}": d for d in items}
    selected_label = st.selectbox("选择部门", list(options.keys()))
    selected = options[selected_label]

    # 用部门编码做 key 后缀：切换到另一个部门时，表单会重新取该部门的值。
    # 如果不加 key，Streamlit 会沿用上一个部门的输入，这是常见坑。
    key_suffix = selected["dept_code"]

    with st.form("edit_dept"):
        full_name = st.text_input(
            "部门名称",
            value=selected.get("full_name", ""),
            key=f"edit_full_name_{key_suffix}",
        )
        address = st.text_input(
            "地址",
            value=selected.get("address") or "",
            key=f"edit_address_{key_suffix}",
        )

        col1, col2 = st.columns(2)
        with col1:
            longitude = st.number_input(
                "经度",
                value=float(selected.get("longitude") or 0),
                format="%.3f",
                key=f"edit_longitude_{key_suffix}",
            )
        with col2:
            latitude = st.number_input(
                "纬度",
                value=float(selected.get("latitude") or 0),
                format="%.3f",
                key=f"edit_latitude_{key_suffix}",
            )

        parent_dept_code = st.text_input(
            "父部门编码",
            value=selected.get("parent_dept_code") or "",
            key=f"edit_parent_{key_suffix}",
        )
        save = st.form_submit_button("保存修改")

    if save:
        try:
            api.put(
                f"/departments/{selected['dept_code']}",
                json={
                    "full_name": full_name,
                    "address": address or None,
                    "longitude": longitude,
                    "latitude": latitude,
                    "parent_dept_code": parent_dept_code or None,
                },
            )
            st.success("修改成功")
            st.rerun()
        except api.ApiError as exc:
            st.error(exc.detail)

    with st.expander("删除部门（危险操作）"):
        st.caption(f"将删除：{selected['dept_code']} - {selected['full_name']}")
        confirm = st.checkbox(
            "我确认要删除该部门",
            key=f"dept_delete_confirm_{selected['dept_code']}",
        )
        if st.button("删除", type="primary", disabled=not confirm):
            try:
                api.delete(f"/departments/{selected['dept_code']}")
                st.success("删除成功")
                st.rerun()
            except api.ApiError as exc:
                st.error(exc.detail)
