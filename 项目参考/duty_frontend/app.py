"""应用入口：登录门禁 + 首页。

启动方式（在 duty_frontend 目录下）：
    streamlit run app.py

页面导航由 pages/ 目录自动生成，左侧边栏显示五个模块页面。
"""

import streamlit as st

import api_client as api
import auth
import ui

st.set_page_config(
    page_title="执勤电子年鉴",
    page_icon="🗂️",
    layout="wide",
)
ui.inject_css()

# 未登录：只显示登录页，不渲染首页内容
if not auth.is_logged_in():
    auth.render_login()
    st.stop()

auth.render_user_box()
ui.show_flash()

user = auth.current_user()

# ---------------------------------------------------------------------------
# 顶部横幅
# ---------------------------------------------------------------------------
ui.hero(
    "执勤电子年鉴",
    "从登录、基础数据维护到执勤统计的完整前后端链路",
    badge=f"当前用户：{user.get('username', '-')} · {user.get('role', '-')}",
)

# ---------------------------------------------------------------------------
# 功能卡片：与后端四表 + 统计一一对应
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    ui.feature_card(
        "单位管理",
        "单位的查询、分页、新增、编辑与删除，是通用 CRUD 页面的样板。",
        "🏢",
    )
with col2:
    ui.feature_card(
        "人员与哨位",
        "人员按单位筛选，哨位有启用状态；两者都维护对外键的引用。",
        "👤",
    )
with col3:
    ui.feature_card(
        "执勤与统计",
        "登记执勤记录，按人员和年份查看执勤天数、时长与时段分布。",
        "📊",
    )

st.write("")

# ---------------------------------------------------------------------------
# 运行状态 + 快速开始
# ---------------------------------------------------------------------------
left, right = st.columns([1.25, 1])

with left:
    with st.container(border=True):
        st.subheader("系统状态")
        try:
            status = api.health()
            st.success(f"后端服务正常：{status.get('status', 'ok')}")
        except api.ApiError as exc:
            st.error(exc.detail)
            st.caption("请先在 duty-simplified 目录启动后端：`python main.py`")
        st.caption(f"后端地址：{api.API_BASE_URL}")

with right:
    with st.container(border=True):
        st.subheader("快速开始")
        st.markdown(
            "1. 左侧选择「单位管理」，查看示例单位\n"
            "2. 依次录入人员、哨位，再登记一条执勤记录\n"
            "3. 打开「数据统计」，选择人员和 2026 年"
        )

st.divider()
st.caption("参考实现：duty_frontend（Streamlit）→ duty-simplified（FastAPI）")
