"""数据统计页：指标卡 + 时间分布折线图 + 月度值班柱状图。

对应课次 19、20、21：
- 人员下拉框来自 GET /api/v1/personnel；
- 指标卡与图表来自 /api/v1/analytics 下的三个接口：
    * staff-duty-yearly      年度总天数、总时长、月度分布
    * duty-time-distribution 24 小时时间分布、高峰时段
    * contribution-ranking   部门排名、贡献度
- 所有接口都需要 Authorization: Bearer <token>，由 api_client 自动注入。

说明：duty 的后端没有"某人员在各站点分布"的接口；
workstation-duty-yearly 是按工位统计，需要 workstation_id，故不作为本页主图。
"""

import pandas as pd
import streamlit as st

import api_client as api
import auth

st.set_page_config(page_title="数据统计", page_icon="📊", layout="wide")
auth.require_login()
auth.render_user_box()

st.title("📊 数据统计")

# ---------------------------------------------------------------------------
# 1. 选择人员与年份
# ---------------------------------------------------------------------------
try:
    with st.spinner("正在加载人员列表..."):
        personnel_data = api.get("/personnel", params={"page": 1, "page_size": 100})
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

items = personnel_data.get("items", [])
if not items:
    st.warning("暂无人员数据，请先在后台录入人员")
    st.stop()

options = {f"{p['name']}（{p['certificate_number']}）": p for p in items}
selected_label = st.selectbox("选择人员", list(options.keys()))
person = options[selected_label]
certificate_number = person["certificate_number"]

col1, col2 = st.columns([1, 2])
with col1:
    # 示例数据集中在 2025 年；实际使用时改成需要统计的年份
    year = st.text_input("年份", value="2025", max_chars=4)

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
        ranking = api.get("/analytics/contribution-ranking", params=params)
except api.ApiError as exc:
    st.error(exc.detail)
    st.stop()

# ---------------------------------------------------------------------------
# 3. 指标卡
# ---------------------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("总值班天数", yearly.get("total_duty_days", 0))
m2.metric("总值班时长（小时）", yearly.get("total_duty_hours", 0))
m3.metric("部门排名", ranking.get("ranking", "-"))
m4.metric("贡献度", ranking.get("contribution_percentage", "-"))

st.caption(
    f"{yearly.get('personnel_name', person['name'])} · {year} 年 · "
    f"部门平均 {ranking.get('dept_average_hours', '-')} 小时 · "
    f"部门共 {ranking.get('total_staff_count', '-')} 人"
)

st.divider()

# ---------------------------------------------------------------------------
# 4. 图 1：24 小时值班时间分布
# ---------------------------------------------------------------------------
st.subheader("值班时间段分布")
time_rows = distribution.get("time_distribution", [])
if time_rows:
    df_time = pd.DataFrame(time_rows).set_index("hour")
    df_time.index.name = "小时"
    st.line_chart(df_time, y="count")

    peak_hours = distribution.get("peak_hours", [])
    if peak_hours:
        st.caption("高峰时段：" + "、".join(f"{h}:00" for h in peak_hours))
    st.caption(f"统计口径：{distribution.get('total_records', 0)} 条值班记录")
else:
    st.info("该年度暂无值班记录")

# ---------------------------------------------------------------------------
# 5. 图 2：月度值班分布
# ---------------------------------------------------------------------------
st.subheader("月度值班分布")
month_rows = yearly.get("duty_by_month", [])
if month_rows:
    df_month = pd.DataFrame(month_rows).set_index("month")
    df_month.index.name = "月份"
    st.bar_chart(df_month, y="days")
else:
    st.info("该年度暂无月度数据")

st.caption("数据来源：值班数据统计服务 /api/v1/analytics")
