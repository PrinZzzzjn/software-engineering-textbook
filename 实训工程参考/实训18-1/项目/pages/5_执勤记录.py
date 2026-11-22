"""实训 18-1 执勤记录页：筛选、分页、新增与删除。

执勤记录的后端没有 PUT 接口，因此本页只做新增与删除；
要调整时段就删除后重建，这正是「先看接口契约再写页面」的例子。

新增时后端会按顺序校验：开始早于结束 → 人员与哨位存在 → 同一哨位时段不重叠。
前端只做「必填 + 时间先后」这类不查库的检查，冲突仍交给后端判定。
"""

from datetime import date, datetime, time

import streamlit as st

import api_client as api
import auth
from components.feedback import set_flash, show_flash
from components.table import pagination_bar, render_table
from config import DEFAULT_PAGE_SIZE

st.set_page_config(page_title="执勤记录", page_icon="📋", layout="wide")

auth.require_login()
auth.render_user_box()

st.title("📋 执勤记录")
st.caption("按人员与哨位筛选执勤记录，支持新增与删除；后端不提供修改接口。")
show_flash()

# ---------- 人员与哨位下拉 ----------
try:
    personnel = api.get(
        "/personnel", params={"page": 1, "page_size": 100}
    ).get("items", [])
    workstations = api.get(
        "/workstations", params={"page": 1, "page_size": 100}
    ).get("items", [])
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

person_options = {
    f"{p['certificate_number']} - {p['name']}": p["certificate_number"]
    for p in personnel
}
station_options = {
    f"{w['workstation_id']} - {w['name']}": w["workstation_id"]
    for w in workstations
}

if "duty_page" not in st.session_state:
    st.session_state["duty_page"] = 1
if "duty_page_size" not in st.session_state:
    st.session_state["duty_page_size"] = DEFAULT_PAGE_SIZE
if "duty_person" not in st.session_state:
    st.session_state["duty_person"] = "全部"
if "duty_station" not in st.session_state:
    st.session_state["duty_station"] = "全部"

# ---------- 筛选区 ----------
with st.container(border=True):
    col_person, col_station, col_size = st.columns([2, 2, 1])
    with col_person:
        person_label = st.selectbox(
            "人员", ["全部"] + list(person_options.keys()), key="duty_person"
        )
    with col_station:
        station_label = st.selectbox(
            "哨位", ["全部"] + list(station_options.keys()), key="duty_station"
        )
    with col_size:
        page_size = st.selectbox(
            "每页条数", [5, DEFAULT_PAGE_SIZE, 20], key="duty_page_size"
        )

signature = f"{person_label}|{station_label}|{page_size}"
if st.session_state.get("duty_query_signature") != signature:
    st.session_state["duty_query_signature"] = signature
    st.session_state["duty_page"] = 1

page = st.session_state["duty_page"]

params = {"page": page, "page_size": page_size}
if person_label != "全部":
    params["personnel_certificate_number"] = person_options[person_label]
if station_label != "全部":
    params["workstation_id"] = station_options[station_label]

try:
    with st.spinner("正在加载执勤记录..."):
        data = api.get("/duty-records", params=params)
except api.ApiError as exc:
    if exc.status_code == 401:
        st.session_state["login_notice"] = exc.detail
        st.rerun()
    st.error(exc.detail)
    st.stop()

items = data.get("items", [])
total = data.get("total", 0)

if not items and page > 1:
    st.session_state["duty_page"] = page - 1
    st.rerun()

# ---------- 内容区 ----------
st.subheader("记录列表")
metric_total, metric_page = st.columns(2)
metric_total.metric("记录数（当前条件）", total)
metric_page.metric("本页显示", len(items))

if not items:
    st.info("没有符合条件的执勤记录。可清空筛选，或在下方「新增记录」补充。")
else:
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
        column_config={
            "id": st.column_config.NumberColumn("编号", width="small"),
            "personnel_certificate_number": st.column_config.TextColumn(
                "证件号", width="small"
            ),
            "workstation_id": st.column_config.TextColumn("哨位", width="small"),
            "start_time": st.column_config.TextColumn("开始时间", width="large"),
            "end_time": st.column_config.TextColumn("结束时间", width="large"),
            "status": st.column_config.TextColumn("状态", width="small"),
        },
    )
    new_page = pagination_bar(total, page, page_size, "duty")
    if new_page != page:
        st.session_state["duty_page"] = new_page
        st.rerun()

# ---------- 操作区：新增 ----------
st.subheader("新增记录")
with st.container(border=True):
    if not person_options or not station_options:
        st.info("请先准备人员与哨位数据。")
    else:
        with st.form("create_duty_record", clear_on_submit=True):
            new_person = st.selectbox(
                "人员 *", list(person_options.keys()), key="new_duty_person"
            )
            new_station = st.selectbox(
                "哨位 *", list(station_options.keys()), key="new_duty_station"
            )
            col_start_date, col_start_time = st.columns(2)
            with col_start_date:
                start_date = st.date_input(
                    "开始日期", value=date(2026, 5, 1), key="new_duty_start_date"
                )
            with col_start_time:
                start_time = st.time_input(
                    "开始时间", value=time(8, 0), key="new_duty_start_time"
                )
            col_end_date, col_end_time = st.columns(2)
            with col_end_date:
                end_date = st.date_input(
                    "结束日期", value=date(2026, 5, 1), key="new_duty_end_date"
                )
            with col_end_time:
                end_time = st.time_input(
                    "结束时间", value=time(12, 0), key="new_duty_end_time"
                )
            status = st.text_input("状态", value="normal", key="new_duty_status")
            submitted = st.form_submit_button(
                "提交", type="primary", key="create_duty_submit"
            )

        if submitted:
            start_dt = datetime.combine(start_date, start_time)
            end_dt = datetime.combine(end_date, end_time)
            if start_dt >= end_dt:
                st.error("开始时间必须早于结束时间")
            else:
                try:
                    api.post(
                        "/duty-records",
                        json={
                            "personnel_certificate_number": person_options[
                                new_person
                            ],
                            "workstation_id": station_options[new_station],
                            "start_time": start_dt.isoformat(),
                            "end_time": end_dt.isoformat(),
                            "status": status.strip() or "normal",
                        },
                    )
                except api.ApiError as exc:
                    if exc.status_code == 401:
                        st.session_state["login_notice"] = exc.detail
                        st.rerun()
                    st.error(exc.detail)
                else:
                    st.session_state["duty_page"] = 1
                    set_flash("已新增执勤记录")
                    st.rerun()

# ---------- 操作区：删除 ----------
st.subheader("删除记录")
with st.container(border=True):
    if not items:
        st.info("当前页没有可删除的执勤记录。")
    else:
        delete_options = {
            f"#{r['id']} {r['personnel_certificate_number']} "
            f"{r['start_time']} → {r['end_time']}": r["id"]
            for r in items
        }
        delete_label = st.selectbox(
            "选择记录", list(delete_options.keys()), key="duty_delete_select"
        )
        target_id = delete_options[delete_label]

        st.caption("删除不可撤销；如需调整时段，请删除后重新新增。")
        with st.expander("删除记录（危险操作）"):
            st.caption(f"将删除记录 #{target_id}")
            confirm = st.checkbox(
                "我确认要删除该记录", key=f"duty_delete_confirm_{target_id}"
            )
            if st.button(
                "删除", type="primary", disabled=not confirm, key="duty_delete"
            ):
                try:
                    api.delete(f"/duty-records/{target_id}")
                except api.ApiError as exc:
                    if exc.status_code == 401:
                        st.session_state["login_notice"] = exc.detail
                        st.rerun()
                    st.error(exc.detail)
                else:
                    set_flash(f"已删除执勤记录 #{target_id}")
                    st.rerun()
