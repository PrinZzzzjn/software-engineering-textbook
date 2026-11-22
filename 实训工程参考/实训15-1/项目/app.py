"""实训 15-1 单位管理页：四类组件 + 指标 + 表格 + 筛选 + 新增（假数据）。

启动（在本目录下）：
    python -m streamlit run app.py

本章不接后端：数据来自 SEED_DEPARTMENTS，新增结果写回 st.session_state。
字段与接口契约一致：dept_code / full_name / address。
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="单位管理", page_icon="🏢", layout="wide")

SEED_DEPARTMENTS = [
    {"dept_code": "D001", "full_name": "一中队", "address": "一号营区"},
    {"dept_code": "D002", "full_name": "二中队", "address": "二号营区"},
    {"dept_code": "D003", "full_name": "三中队", "address": "三号营区"},
    {"dept_code": "D004", "full_name": "四中队", "address": "四号营区"},
    {"dept_code": "D005", "full_name": "五中队", "address": "五号营区"},
    {"dept_code": "D006", "full_name": "勤务保障中队", "address": "综合楼 201"},
    {"dept_code": "D007", "full_name": "通信保障中队", "address": "通信楼 101"},
    {"dept_code": "D008", "full_name": "卫生队", "address": "医务楼"},
    {"dept_code": "D009", "full_name": "运输保障中队", "address": "车库楼"},
    {"dept_code": "D010", "full_name": "警戒分队", "address": "门岗楼"},
    {"dept_code": "D011", "full_name": "教导队", "address": "教学楼"},
    {"dept_code": "D012", "full_name": "装备保障中队", "address": ""},
]


def _init_state() -> None:
    """第一次运行时把假数据放进 session_state；之后新增都写这一份。"""
    if "departments" not in st.session_state:
        st.session_state.departments = [row.copy() for row in SEED_DEPARTMENTS]


def _filter(items, keyword: str, only_with_address: bool):
    keyword = keyword.strip().lower()
    result = []
    for item in items:
        if keyword and keyword not in item["dept_code"].lower() and keyword not in item["full_name"].lower():
            continue
        if only_with_address and not (item.get("address") or "").strip():
            continue
        result.append(item)
    return result


def _clear_keyword() -> None:
    """按钮回调：在脚本重跑前把搜索词清空。"""
    st.session_state["keyword"] = ""


_init_state()

st.title("🏢 单位管理")
st.caption("第 15 章实训：假数据版本，不接后端。输入、展示、交互、容器四类组件各至少用一个。")

# 新增成功后先写入提示，再 rerun；重跑后在这里显示，避免表格先于新增渲染
flash = st.session_state.pop("flash_message", None)
if flash:
    st.success(flash)

all_items = st.session_state.departments

# ----------------------------- 筛选区 -------------------------------------
left, right = st.columns([3, 1])
with left:
    keyword = st.text_input(
        "搜索单位",
        placeholder="输入单位编码或名称，例如 D001 / 一中队",
        key="keyword",
    )
with right:
    only_with_address = st.checkbox("只看有地址的单位", key="only_with_address")
    st.button("清空搜索", key="clear_keyword", on_click=_clear_keyword)

filtered = _filter(all_items, keyword, only_with_address)

# ----------------------------- 指标区 -------------------------------------
metric_total, metric_address, metric_filtered = st.columns(3)
metric_total.metric("单位总数", len(all_items))
metric_address.metric(
    "已填地址", sum(1 for item in all_items if (item.get("address") or "").strip())
)
metric_filtered.metric("当前筛选结果", len(filtered))

st.divider()

tab_list, tab_create = st.tabs(["📋 单位列表", "➕ 新增单位"])

# ----------------------------- 列表区 -------------------------------------
with tab_list:
    if filtered:
        table = pd.DataFrame(filtered)[["dept_code", "full_name", "address"]]
        dept_config = {
            "dept_code": st.column_config.TextColumn("单位编码", width="small"),
            "full_name": st.column_config.TextColumn("单位名称"),
            "address": st.column_config.TextColumn("地址", width="large"),
        }
        st.dataframe(
            table,
            width="stretch",
            hide_index=True,
            column_config=dept_config,
        )
        st.download_button(
            "导出当前结果 CSV",
            data=table.to_csv(index=False).encode("utf-8-sig"),
            file_name="departments.csv",
            mime="text/csv",
            key="download_departments",
        )
    else:
        st.info("没有符合条件的单位，请调整搜索条件或取消筛选。")

# ----------------------------- 新增区 -------------------------------------
with tab_create:
    st.caption("带 * 的为必填项。单位编码创建后不可修改。")
    with st.form("create_department", clear_on_submit=True):
        col_code, col_name = st.columns(2)
        with col_code:
            dept_code = st.text_input(
                "单位编码 *", placeholder="例如 D013", key="new_dept_code"
            )
        with col_name:
            full_name = st.text_input("单位名称 *", key="new_full_name")
        address = st.text_input("地址", key="new_address")
        submitted = st.form_submit_button("提交", type="primary", key="submit_dept")

    if submitted:
        code = dept_code.strip()
        name = full_name.strip()
        if not code or not name:
            st.error("单位编码和单位名称不能为空")
        elif any(item["dept_code"] == code for item in st.session_state.departments):
            st.error(f"单位编码 {code} 已存在")
        else:
            st.session_state.departments.append(
                {
                    "dept_code": code,
                    "full_name": name,
                    "address": address.strip(),
                }
            )
            st.session_state["flash_message"] = f"已新增单位 {code} - {name}"
            st.rerun()

st.divider()
st.caption("假数据仅用于界面验证；第 16 章把同一页面接到真实接口。")
