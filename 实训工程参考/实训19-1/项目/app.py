"""实训 19-1 应用入口：首页 + 登录门禁。

启动（在本目录下）：
    python -m streamlit run app.py

页面导航由 pages/ 目录自动生成，不需要手写菜单：
    pages/1_单位管理.py → 单位管理
    pages/2_数据统计.py → 数据统计
    pages/3_人员管理.py → 人员管理
    pages/4_哨位管理.py → 哨位管理
    pages/5_执勤记录.py → 执勤记录

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
        - **单位管理**：查询、分页、新增、编辑与删除单位
        - **数据统计**：指标卡 + 24 小时折线图 + 月度柱状图 + 执勤明细
        - **人员管理**：按姓名与单位筛选，维护人员信息
        - **哨位管理**：按单位筛选，维护哨位与启用状态
        - **执勤记录**：按人员与哨位筛选，新增与删除执勤时段
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
st.caption(
    "实训 19-1：主题与图表色统一；统计页按「总览—趋势—明细」组织，指标数字全部来自接口。"
)
