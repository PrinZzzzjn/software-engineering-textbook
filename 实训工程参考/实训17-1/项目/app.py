"""实训 17-1 应用入口：首页 + 登录门禁。

启动（在本目录下）：
    python -m streamlit run app.py

页面导航由 pages/ 目录自动生成，不需要手写菜单：
    pages/1_单位管理.py → 单位管理
    pages/2_数据统计.py → 数据统计

入口只负责两件事：门禁与导航说明；页面内容各自放在 pages/ 下。
"""

import streamlit as st

import api_client as api
import auth

st.set_page_config(page_title="执勤电子年鉴", page_icon="🗂️", layout="wide")

# 未登录：只显示登录页，不渲染首页内容
if not auth.is_logged_in():
    auth.render_login()
    st.stop()

auth.render_user_box()

st.title("🗂️ 执勤电子年鉴")
user = auth.current_user()
st.caption(f"欢迎，{user.get('username', '用户')}（{user.get('role', '-')}）")

left, right = st.columns([2, 1])

with left:
    st.subheader("功能导航")
    st.markdown(
        """
        - **单位管理**：单位列表、名称搜索、分页与新增
        - **数据统计**：按人员与年份查看执勤天数、时长与月度分布
        """
    )
    st.caption("左侧边栏由 pages/ 目录自动生成：新增页面只需新增一个 .py 文件。")

with right:
    st.subheader("运行状态")
    try:
        status = api.get("/health")
        st.success(f"后端正常：{status.get('status', 'ok')}")
    except api.ApiError as exc:
        st.error(exc.detail)
        st.caption("请先启动后端：实训 13-1 项目 `python -m uvicorn main:app --port 8000`。")

st.divider()
st.caption("实训 17-1：入口只做门禁与导航说明，页面内容分别放在 pages/ 下。")
