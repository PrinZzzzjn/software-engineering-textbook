"""应用入口：登录门禁 + 首页。

启动方式（在 duty_frontend 目录下）：
    streamlit run app.py

页面导航由 pages/ 目录自动生成，左侧边栏会显示"部门管理""数据统计"。
"""

import streamlit as st

import api_client as api
import auth

st.set_page_config(
    page_title="值班数据统计系统",
    page_icon="🗂️",
    layout="wide",
)

# 未登录：只显示登录页，不渲染首页内容
if not auth.is_logged_in():
    auth.render_login()
    st.stop()

auth.render_user_box()

st.title("🗂️ 值班数据统计系统")
user = auth.current_user()
st.caption(f"欢迎，{user.get('username', '用户')}（{user.get('role', '-')}）")

left, right = st.columns(2)

with left:
    st.subheader("系统功能")
    st.markdown(
        """
        - **部门管理**：部门列表、搜索、分页、新增、编辑、删除
        - **数据统计**：个人值班时间分布、月度值班统计、贡献度排名

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
        st.caption("请先启动后端：在 duty 目录执行 `python main.py` 或 `uvicorn main:app --port 8000`。")

    st.caption(f"后端地址：{api.API_BASE_URL}")

st.divider()
st.caption("参考实现：duty_frontend（Streamlit 前端）→ duty（FastAPI 后端）")
