from pathlib import Path
import sys

import streamlit as st

TOOLS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from case_data import (  # noqa: E402
    ROOT,
    apply_changes,
    build_json,
    load_source,
    save_source,
    scan_aliases,
    set_field,
)

DATASET_LABELS = {
    "baseline": "基准种子",
    "teaching_simplified": "旧值映射",
    "verification": "验证临时",
    "frontend_demo": "前端演示",
}


def _source_path() -> Path:
    raw = st.query_params.get("source")
    if raw:
        return Path(raw)
    return ROOT / "data" / "case_data.yaml"


def _output_path() -> Path:
    raw = st.query_params.get("source")
    if raw:
        return Path(raw).parent / "case_data.json"
    return ROOT / "data" / "case_data.json"


def render_editor() -> None:
    st.set_page_config(page_title="执勤电子年鉴 · 案例数据管理", page_icon="🗂️", layout="wide")
    st.title("执勤电子年鉴 · 案例数据管理")
    source_path = _source_path()
    doc = load_source(source_path)

    with st.sidebar:
        st.header("数据集")
        dataset = st.radio(
            "数据集",
            list(DATASET_LABELS),
            format_func=lambda k: DATASET_LABELS[k],
            key="dataset",
        )

    entities = doc["datasets"][dataset].get("entities", {})
    if not entities:
        st.info("这个数据集暂无实体。")
        entity = None
        rows = []
        ids = []
    else:
        entity = st.selectbox("实体类型", list(entities), key="entity")
        items = entities[entity]
        rows = [
            {"ID": item["id"], **{k: v for k, v in item["fields"].items() if isinstance(v, (str, int, float))}}
            for item in items
        ]
        st.dataframe(rows, hide_index=True, width="stretch")
        ids = [item["id"] for item in items]

    selected_id = st.selectbox("选择记录", ids, key="record_id") if ids else None
    if selected_id:
        selected = next(item for item in entities[entity] if item["id"] == selected_id)
        st.subheader(f"编辑 {selected_id}")
        with st.form("edit_form", clear_on_submit=False):
            new_values = {}
            for key, value in selected["fields"].items():
                new_values[key] = st.text_input(
                    key,
                    value=str(value),
                    key=f"edit_{dataset}_{entity}_{selected_id}_{key}",
                )
            saved = st.form_submit_button("保存修改", key="save_field", type="primary")
        if saved:
            for key, value in new_values.items():
                if key == "is_active":
                    try:
                        value = int(value)
                    except ValueError:
                        st.error(f"{key} 必须是 0 或 1")
                        st.stop()
                set_field(doc, dataset, entity, selected_id, key, value)
            save_source(doc, source_path)
            build_json(doc, _output_path())
            st.success("已保存并生成运行副本")

    st.divider()
    st.subheader("同步与检查")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("生成运行副本", key="build_json"):
            build_json(load_source(source_path), _output_path())
            st.success("已生成 case_data.json")
    with c2:
        if st.button("检查引用", key="check_refs"):
            hits = scan_aliases(ROOT, load_source(source_path))
            st.info(f"待同步引用 {len(hits)} 处")
            for h in hits[:20]:
                st.caption(f"{h['file']}:{h['line']} {h['old']} → {h['new']}")
    with c3:
        confirmed = st.checkbox("我已确认变更清单", key="confirm_apply")
        if st.button("应用到全仓", key="apply_all", disabled=not confirmed):
            # 以当前页面编辑的事实源为准扫描整仓
            active_rules = load_source(source_path)
            changes = apply_changes(ROOT, yes=False, source=active_rules)
            st.warning(f"将修改 {len(changes)} 个文件；请先在 CLI 用 diff 查看完整清单")
            if confirmed:
                applied = apply_changes(ROOT, yes=True, source=active_rules)
                st.success(f"已应用 {len(applied)} 个文件的修改")


render_editor()
