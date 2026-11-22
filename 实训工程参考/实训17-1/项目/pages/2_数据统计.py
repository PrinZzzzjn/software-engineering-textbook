"""实训 17-1 数据统计页：按人员与年份查看执勤汇总。

数据来源（接口契约见 _shared/接口契约清单.md）：
    GET /personnel                         人员下拉
    GET /analytics/staff-duty-yearly       年度汇总与月度分布
    GET /analytics/duty-time-distribution  24 小时分布

本页只用指标与表格；图表留到 19-1。
"""

import streamlit as st

import api_client as api
import auth
from components.table import render_table

st.set_page_config(page_title="数据统计", page_icon="📊", layout="wide")

# 访问守卫：直接输入子页面地址也绕不过登录
auth.require_login()
auth.render_user_box()

# ---------- 标题区 ----------
st.title("📊 数据统计")
st.caption("选择人员与年份，查看执勤天数、时长、月度分布与 24 小时分布。")

# ---------- 筛选区 ----------
with st.container(border=True):
    col_person, col_year = st.columns([2, 1])
    with col_person:
        try:
            with st.spinner("正在加载人员..."):
                personnel = api.get(
                    "/personnel", params={"page": 1, "page_size": 100}
                ).get("items", [])
        except api.ApiError as exc:
            st.error(exc.detail)
            st.stop()

        options = {
            f"{p['certificate_number']} - {p['name']}": p["certificate_number"]
            for p in personnel
        }
        if not options:
            st.info("没有可统计的人员，请先在人员管理中录入。")
            st.stop()
        label = st.selectbox("人员", list(options.keys()), key="stats_person")

    with col_year:
        year = st.selectbox("年份", ["2026", "2025"], key="stats_year")

cert = options[label]

# ---------- 内容区 ----------
try:
    with st.spinner("正在统计..."):
        yearly = api.get(
            "/analytics/staff-duty-yearly",
            params={"personnel_certificate_number": cert, "year": year},
        )
        dist = api.get(
            "/analytics/duty-time-distribution",
            params={"personnel_certificate_number": cert, "year": year},
        )
except api.ApiError as exc:
    # 400：年份格式错误或人员不存在
    st.error(exc.detail)
    st.stop()

st.subheader("年度汇总")
m_days, m_hours, m_records = st.columns(3)
m_days.metric("执勤天数", yearly.get("total_duty_days", 0))
m_hours.metric("执勤时长（小时）", yearly.get("total_duty_hours", 0))
m_records.metric("记录条数", dist.get("total_records", 0))

left, right = st.columns([3, 2])

with left:
    st.subheader("月度分布")
    monthly = [
        row
        for row in yearly.get("duty_by_month", [])
        if row.get("days") or row.get("hours")
    ]
    if not monthly:
        st.info(f"{year} 年该人员没有执勤记录。")
    else:
        render_table(
            monthly,
            columns=["month", "days", "hours"],
            column_config={
                "month": st.column_config.NumberColumn("月份", width="small"),
                "days": st.column_config.NumberColumn("天数", width="small"),
                "hours": st.column_config.NumberColumn("时长（小时）", format="%.2f"),
            },
        )

with right:
    st.subheader("24 小时分布")
    peak = dist.get("peak_hours") or []
    st.caption(
        "高峰时段：" + ("、".join(f"{hour} 时" for hour in peak) if peak else "无")
    )
    hours = [
        row for row in dist.get("time_distribution", []) if row.get("count")
    ]
    if not hours:
        st.info("没有可展示的时段记录。")
    else:
        render_table(
            hours,
            columns=["hour", "count"],
            column_config={
                "hour": st.column_config.NumberColumn("开始小时", width="small"),
                "count": st.column_config.NumberColumn("记录数", width="small"),
            },
        )
