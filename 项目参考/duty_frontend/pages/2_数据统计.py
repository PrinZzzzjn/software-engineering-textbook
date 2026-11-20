"""数据统计页：指标卡 + 时间分布折线图 + 月度执勤柱状图。

对应第 19 章（界面优化与数据可视化）：
- 人员下拉框来自 GET /personnel；
- 指标与图表来自 analytics 模块的两个只读聚合接口：
    * staff-duty-yearly      年度总天数、总时长、月度分布
    * duty-time-distribution 24 小时时间分布、高峰时段
- 两个接口都需要 personnel_certificate_number 与 year 两个查询参数，
  由 api_client 自动注入 Bearer 令牌。

后端 analytics 模块只有这两个接口，没有部门排名 / 贡献度接口；
指标卡的数据全部来自接口返回字段，不在前端手写。
"""

import pandas as pd
import streamlit as st

import api_client as api
import auth
import ui

st.set_page_config(page_title="数据统计", page_icon="📊", layout="wide")
ui.inject_css()
auth.require_login()
auth.render_user_box()
ui.show_flash()

ui.page_header(
    "数据统计",
    "选择人员与年份，查看执勤时长、24 小时分布与月度统计。",
    "📊",
)

# ---------------------------------------------------------------------------
# 1. 筛选条件（卡片）
# ---------------------------------------------------------------------------
try:
    with st.spinner("正在加载人员列表..."):
        personnel_data = api.get("/personnel", params={"page": 1, "page_size": 100})
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

items = personnel_data.get("items", [])
if not items:
    st.warning("暂无人员数据，请先在「人员管理」录入人员")
    st.stop()

with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        options = {f"{p['name']}（{p['certificate_number']}）": p for p in items}
        selected_label = st.selectbox("选择人员", list(options.keys()))
        person = options[selected_label]
        certificate_number = person["certificate_number"]
    with col2:
        # 演示数据集中在 2026 年
        year = st.text_input("年份", value="2026", max_chars=4)

if len(year) != 4 or not year.isdigit():
    st.error("年份格式应为 YYYY")
    st.stop()

params = {"personnel_certificate_number": certificate_number, "year": year}

# ---------------------------------------------------------------------------
# 2. 拉取统计数据
# ---------------------------------------------------------------------------
try:
    with st.spinner("正在统计数据..."):
        yearly = api.get("/analytics/staff-duty-yearly", params=params)
        distribution = api.get("/analytics/duty-time-distribution", params=params)
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

# ---------------------------------------------------------------------------
# 3. KPI 卡片：字段全部来自接口返回
# ---------------------------------------------------------------------------
peak_hours = distribution.get("peak_hours", [])
peak_text = "、".join(f"{h}:00" for h in peak_hours) if peak_hours else "-"

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
    distribution.get("total_records", 0),
    icon="📋",
    border=True,
    format="%d",
)
m4.metric("高峰时段", peak_text, icon="⏰", border=True)

st.caption(
    f"{person['name']} · {certificate_number} · {year} 年 · "
    f"统计口径：按执勤开始日期去重计天，跨天记录累加时长"
)

# ---------------------------------------------------------------------------
# 4. 两张图表：并排放在带边框的卡片里
# ---------------------------------------------------------------------------
left, right = st.columns(2)

# ---- 图 1：24 小时执勤时间分布 ----
with left:
    with st.container(border=True):
        st.subheader("24 小时执勤分布")
        st.caption("按执勤开始时间的小时统计")

        time_rows = distribution.get("time_distribution", [])
        if time_rows:
            df_time = pd.DataFrame(time_rows).set_index("hour")
            df_time.index.name = "小时"
            st.line_chart(
                df_time,
                y="count",
                color=ui.CHART_COLOR,
                height=260,
            )

            if peak_hours:
                st.caption("高峰时段：" + "、".join(f"{h}:00" for h in peak_hours))
            st.caption(f"统计口径：{distribution.get('total_records', 0)} 条执勤记录")

            with st.expander("查看数据表"):
                st.dataframe(df_time.reset_index(), width="stretch", hide_index=True)
        else:
            st.info("该年度暂无执勤记录")

# ---- 图 2：月度执勤分布 ----
with right:
    with st.container(border=True):
        st.subheader("月度执勤分布")
        st.caption("每月执勤天数")

        month_rows = yearly.get("duty_by_month", [])
        if month_rows:
            df_month = pd.DataFrame(month_rows).set_index("month")
            df_month.index.name = "月份"
            st.bar_chart(
                df_month,
                y="days",
                color=ui.CHART_COLOR,
                height=260,
            )

            with st.expander("查看数据表"):
                st.dataframe(df_month.reset_index(), width="stretch", hide_index=True)
        else:
            st.info("该年度暂无月度数据")

st.caption("数据来源：执勤统计分析服务 /analytics")
