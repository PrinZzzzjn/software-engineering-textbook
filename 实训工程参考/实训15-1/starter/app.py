"""实训 15-1 起点：第 14 章的单页骨架。

运行（在本目录下）：
    python -m streamlit run app.py

本文件只有页面配置和标题。按教材 15.2 的组件分类与 15.3 的实训步骤，
依次补：指标、表格、筛选、空态、新增表单。
"""

import streamlit as st

st.set_page_config(page_title="单位管理", page_icon="🏢", layout="wide")

st.title("🏢 单位管理")
st.caption("第 15 章实训：假数据版本，不接后端。")

st.info("待完成：指标卡、单位表格、搜索与筛选、空态提示、新增表单。")
