"""应用入口：登录门禁 + 首页（基础版）。

启动方式（在 duty_frontend_basic 目录下）：
    streamlit run app.py

页面导航由 pages/ 目录自动生成，左侧边栏显示五个模块页面。
"""

import streamlit as st

import api_client as api
import auth

st.set_page_config(
    page_title="执勤电子年鉴",
    page_icon="🗂️",
    layout="wide",
)

# 未登录：只显示登录页，不渲染首页内容
if not auth.is_logged_in():
    auth.render_login()
    st.stop()

auth.render_user_box()

st.title("🗂️ 执勤电子年鉴")
user = auth.current_user()
st.caption(f"欢迎，{user.get('username', '用户')}（{user.get('role', '-')}）")

left, right = st.columns(2)

with left:
    st.subheader("系统功能")
    st.markdown(
        """
        - **单位管理**：单位列表、分页、新增、编辑、删除
        - **数据统计**：执勤天数、时长、24 小时分布与月度统计
        - **人员管理**：按单位筛选的人员维护
        - **哨位管理**：哨位与启用状态维护
        - **执勤记录**：执勤安排登记与时段冲突检查

        左侧边栏是自动生成的页面导航，对应 `pages/` 目录下的文件。
        """
    )

with right:
    st.subheader("运行状态")
    try:
        status = api.health()
        st.success(f"后端服务正常：{status.get('status', 'ok')}")
    except api.ApiError as exc:
        st.error(exc.detail)
        st.caption("请先启动后端：在 duty-simplified 目录执行 `python main.py`。")

    st.caption(f"后端地址：{api.API_BASE_URL}")

st.divider()
st.caption("参考实现：duty_frontend_basic（Streamlit 前端）→ duty-simplified（FastAPI 后端）")
