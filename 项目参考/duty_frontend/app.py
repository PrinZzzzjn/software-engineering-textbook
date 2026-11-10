"""应用入口：登录门禁 + 首页。

启动方式（在 duty_frontend 目录下）：
    streamlit run app.py

页面导航由 pages/ 目录自动生成，左侧边栏会显示"部门管理""数据统计"。
"""

import streamlit as st

import api_client as api
import auth
import ui

st.set_page_config(
    page_title="值班数据统计系统",
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
    "值班数据统计系统",
    "专题三参考实现 · 从登录、部门管理到数据统计的完整前后端链路",
    badge=f"当前用户：{user.get('username', '-')} · {user.get('role', '-')}",
)

# ---------------------------------------------------------------------------
# 三张功能卡片
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    ui.feature_card(
        "部门管理",
        "列表、搜索、分页、新增、编辑、删除，是通用 CRUD 页面的样板。",
        "🏢",
    )
with col2:
    ui.feature_card(
        "数据统计",
        "个人值班时间分布、月度值班统计与部门贡献度排名。",
        "📊",
    )
with col3:
    ui.feature_card(
        "前后端联调",
        "统一请求封装、登录态管理、错误处理与加载状态。",
        "🔗",
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
            st.caption("请先在 duty 目录启动后端：`python main.py`")
        st.caption(f"后端地址：{api.API_BASE_URL}")

with right:
    with st.container(border=True):
        st.subheader("快速开始")
        st.markdown(
            "1. 左侧选择「部门管理」，查看示例部门\n"
            "2. 试一次新增 / 编辑 / 删除\n"
            "3. 打开「数据统计」，选择人员和 2025 年"
        )

st.divider()
st.caption("参考实现：duty_frontend（Streamlit）→ duty（FastAPI）")
