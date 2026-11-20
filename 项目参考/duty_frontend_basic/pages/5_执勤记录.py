"""执勤记录页：按人员 / 哨位筛选的列表 / 分页 / 新增 / 删除。

接口（对接 duty-simplified）：
- 列表：GET /duty-records?page=&page_size=&personnel_certificate_number=&workstation_id=
- 新增：POST /duty-records
- 删除：DELETE /duty-records/{id}

字段：id（自增主键）/ personnel_certificate_number / workstation_id /
start_time / end_time / status。后端只有新增与删除，没有更新接口，
所以本页不提供编辑。

后端在新增时校验三条规则（违反返回 400）：
1. 开始时间必须早于结束时间；
2. 人员与哨位必须存在；
3. 同一哨位上的执勤时段不得重叠。
"""

from datetime import datetime

import pandas as pd
import streamlit as st

import api_client as api
import auth
from components.table import pagination_bar, render_table

st.set_page_config(page_title="执勤记录", page_icon="📋", layout="wide")
auth.require_login()
auth.render_user_box()

st.title("📋 执勤记录")
st.caption("登记与查询执勤安排：按人员或哨位筛选，检查时段冲突后提交。")


# 人员、哨位下拉选项（用于筛选与新增表单）
try:
    person_data = api.get("/personnel", params={"page": 1, "page_size": 100})
    person_options = [p["certificate_number"] for p in person_data.get("items", [])]
    station_data = api.get("/workstations", params={"page": 1, "page_size": 100})
    station_options = [w["workstation_id"] for w in station_data.get("items", [])]
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

if "record_page" not in st.session_state:
    st.session_state.record_page = 1
if "record_person_filter" not in st.session_state:
    st.session_state.record_person_filter = ""
if "record_station_filter" not in st.session_state:
    st.session_state.record_station_filter = ""

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        person_filter = st.selectbox(
            "按人员筛选",
            options=[""] + person_options,
            key="record_person_filter",
        )
    with col2:
        station_filter = st.selectbox(
            "按哨位筛选",
            options=[""] + station_options,
            key="record_station_filter",
        )

params = {"page": st.session_state.record_page, "page_size": 10}
if person_filter:
    params["personnel_certificate_number"] = person_filter
if station_filter:
    params["workstation_id"] = station_filter

try:
    with st.spinner("正在加载执勤记录..."):
        data = api.get("/duty-records", params=params)
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

items = data.get("items", [])

tab_list, tab_create = st.tabs(["📋 记录列表", "➕ 登记执勤"])

# ----------------------------- 列表 ---------------------------------------
with tab_list:
    if items:
        column_config = {
            "id": st.column_config.NumberColumn("编号", width="small"),
            "personnel_certificate_number": st.column_config.TextColumn("人员证件号"),
            "workstation_id": st.column_config.TextColumn("哨位编号"),
            "start_time": st.column_config.DatetimeColumn("开始时间", format="YYYY-MM-DD HH:mm"),
            "end_time": st.column_config.DatetimeColumn("结束时间", format="YYYY-MM-DD HH:mm"),
            "status": st.column_config.TextColumn("状态"),
        }
        render_table(
            items,
            columns=[
                "id",
                "personnel_certificate_number",
                "workstation_id",
                "start_time",
                "end_time",
                "status",
            ],
            column_config=column_config,
        )
    else:
        st.info("没有符合条件的执勤记录")

    new_page = pagination_bar(
        data.get("total", 0),
        st.session_state.record_page,
        10,
        "record",
    )
    if new_page != st.session_state.record_page:
        st.session_state.record_page = new_page
        st.rerun()

    # 删除（后端无更新接口，只提供删除）
    st.divider()
    with st.expander("删除执勤记录（危险操作）"):
        if not items:
            st.info("当前页没有可删除的记录")
        else:
            options = {f"#{r['id']} · {r['personnel_certificate_number']} · {r['workstation_id']}": r for r in items}
            selected_label = st.selectbox("选择记录", list(options.keys()))
            selected = options[selected_label]
            confirm = st.checkbox(
                "我确认要删除该记录",
                key=f"record_delete_confirm_{selected['id']}",
            )
            if st.button("删除", type="primary", disabled=not confirm):
                try:
                    api.delete(f"/duty-records/{selected['id']}")
                    st.success("执勤记录删除成功")
                    st.rerun()
                except api.ApiError as exc:
                    st.error(exc.detail)

# ----------------------------- 新增 ---------------------------------------
with tab_create:
    st.caption("带 * 的为必填项。同一哨位上已有执勤安排的时段不能重复登记。")
    with st.form("create_duty_record", clear_on_submit=True):
        cert = st.selectbox("人员证件号 *", options=person_options, disabled=not person_options)
        wid = st.selectbox("哨位编号 *", options=station_options, disabled=not station_options)
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("开始日期 *")
            start_time = st.time_input("开始时间 *", value=datetime(2026, 1, 1, 8, 0).time())
        with col2:
            end_date = st.date_input("结束日期 *")
            end_time = st.time_input("结束时间 *", value=datetime(2026, 1, 1, 12, 0).time())
        status = st.selectbox("状态", options=["normal", "abnormal"], format_func=lambda x: "正常" if x == "normal" else "异常")
        submitted = st.form_submit_button("提交", type="primary")

    if submitted:
        if not cert or not wid:
            st.error("请先录入人员与哨位")
        else:
            start_dt = datetime.combine(start_date, start_time)
            end_dt = datetime.combine(end_date, end_time)
            try:
                api.post(
                    "/duty-records",
                    json={
                        "personnel_certificate_number": cert,
                        "workstation_id": wid,
                        "start_time": start_dt.isoformat(),
                        "end_time": end_dt.isoformat(),
                        "status": status,
                    },
                )
                st.success("执勤记录登记成功")
                st.rerun()
            except api.ApiError as exc:
                st.error(exc.detail)
