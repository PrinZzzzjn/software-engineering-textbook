"""实训 19-1 数据统计页：指标卡 + 图表 + 明细的执勤仪表盘。

数据来源（接口契约见 _shared/接口契约清单.md）：
    GET /personnel                         人员下拉
    GET /analytics/staff-duty-yearly       年度汇总与月度分布
    GET /analytics/duty-time-distribution  24 小时分布与高峰时段
    GET /duty-records                      明细（按人员筛选）

信息层级（教材 19.5）：总览（指标卡）→ 趋势与对比（两张图）→ 明细（表格）。
图表颜色 #0D9488 与 .streamlit/config.toml 的主色 #0F766E 同族，全页只用一个图表色。
"""

import pandas as pd
import streamlit as st

import api_client as api
import auth
from components.table import render_table

st.set_page_config(page_title="数据统计", page_icon="📊", layout="wide")

# 访问守卫：直接输入子页面地址也绕不过登录
auth.require_login()
auth.render_user_box()

# 图表色：主色 #0F766E 的邻近色，白底对比度达标（教材 19.4）
CHART_COLOR = "#0D9488"

# ---------- 标题区 ----------
st.title("📊 数据统计")
st.caption("选择人员与年份，先看总览，再看趋势与对比，最后核对明细。")

# ---------- 筛选区：放侧边栏，主区域留给指标与图表 ----------
try:
    with st.spinner("正在加载人员..."):
        personnel = api.get(
            "/personnel", params={"page": 1, "page_size": 100}
        ).get("items", [])
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

if not personnel:
    st.info("没有可统计的人员，请先在人员管理中录入。")
    st.stop()

options = {
    f"{p['certificate_number']} - {p['name']}": p["certificate_number"]
    for p in personnel
}

with st.sidebar:
    st.divider()
    st.subheader("统计筛选")
    label = st.selectbox("人员", list(options.keys()), key="stats_person")
    year = st.selectbox("年份", ["2026", "2025"], key="stats_year")

cert = options[label]

# ---------- 取数区 ----------
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
        records = api.get(
            "/duty-records",
            params={
                "personnel_certificate_number": cert,
                "page": 1,
                "page_size": 100,
            },
        ).get("items", [])
except api.ApiError as exc:
    # 400：年份格式错误或人员不存在
    st.error(exc.detail)
    st.stop()

# ---------- 总览：四个指标卡，数字全部来自接口 ----------
peak_hours = dist.get("peak_hours") or []

m1, m2, m3, m4 = st.columns(4)
m1.metric(
    "总执勤天数",
    yearly.get("total_duty_days", 0),
    icon="📅",
    border=True,
    format="%d",
)
m2.metric(
    "总执勤时长（小时）",
    yearly.get("total_duty_hours", 0),
    icon="⏱️",
    border=True,
    format="%.1f",
)
m3.metric(
    "执勤记录数",
    dist.get("total_records", 0),
    icon="🏅",
    border=True,
    format="%d",
)
m4.metric(
    "高峰时段数",
    len(peak_hours),
    icon="📈",
    border=True,
    format="%d",
)

person_name = next(
    (p["name"] for p in personnel if p["certificate_number"] == cert), cert
)
st.caption(
    f"{person_name} · {cert} · {year} 年｜"
    "统计口径：按执勤开始日期去重计天，时长按结束减开始累加"
)

# ---------- 趋势与对比：两张图并排，各放一张卡片 ----------
left, right = st.columns(2, gap="medium")

with left:
    with st.container(border=True):
        st.subheader("24 小时分布")
        st.caption("按执勤开始时间的小时统计")

        hour_rows = [
            row for row in dist.get("time_distribution", []) if row.get("count")
        ]
        if not hour_rows:
            st.info(f"{year} 年该人员没有执勤记录，暂不绘制分布图。")
        else:
            df_hour = pd.DataFrame(hour_rows).set_index("hour")
            df_hour.index.name = "小时"
            st.line_chart(
                df_hour,
                y="count",
                color=CHART_COLOR,
                height=260,
                width="stretch",
            )
            st.caption(
                "高峰时段："
                + ("、".join(f"{hour} 时" for hour in peak_hours) if peak_hours else "无")
            )
            with st.expander("查看数据表"):
                st.dataframe(
                    df_hour.reset_index(),
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "hour": st.column_config.NumberColumn("小时", width="small"),
                        "count": st.column_config.NumberColumn("记录数", width="small"),
                    },
                )

with right:
    with st.container(border=True):
        st.subheader("月度分布")
        st.caption("每月执勤天数；用于比较各月多少")

        month_rows = yearly.get("duty_by_month", [])
        if not any(row.get("days") or row.get("hours") for row in month_rows):
            st.info(f"{year} 年该人员没有月度数据，暂不绘制柱状图。")
        else:
            df_month = pd.DataFrame(month_rows).set_index("month")
            df_month.index.name = "月份"
            st.bar_chart(
                df_month,
                y="days",
                color=CHART_COLOR,
                height=260,
                width="stretch",
            )
            with st.expander("查看数据表"):
                st.dataframe(
                    df_month.reset_index(),
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "month": st.column_config.NumberColumn("月份", width="small"),
                        "days": st.column_config.NumberColumn("天数", width="small"),
                        "hours": st.column_config.NumberColumn(
                            "时长（小时）", format="%.2f"
                        ),
                    },
                )

# ---------- 明细：图表下方给可核对的数据表 ----------
st.subheader("执勤明细")
detail = [row for row in records if str(row.get("start_time", "")).startswith(year)]
if not detail:
    st.info(f"{year} 年该人员没有执勤明细。")
else:
    detail = sorted(detail, key=lambda row: row.get("start_time", ""))
    render_table(
        detail,
        columns=["id", "workstation_id", "start_time", "end_time", "status"],
        column_config={
            "id": st.column_config.NumberColumn("编号", width="small"),
            "workstation_id": st.column_config.TextColumn("哨位", width="small"),
            "start_time": st.column_config.TextColumn("开始时间", width="large"),
            "end_time": st.column_config.TextColumn("结束时间", width="large"),
            "status": st.column_config.TextColumn("状态", width="small"),
        },
    )

st.caption("数据来源：/analytics/staff-duty-yearly、/analytics/duty-time-distribution 与 /duty-records")
