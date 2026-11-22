# 实训 15-1 完成态项目：单位管理页

单文件 Streamlit 页面，用 12 条单位假数据演示四类组件、指标、表格、筛选、空态与新增。不接后端，新增结果写回 `st.session_state`。

## 运行

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

默认地址 <http://127.0.0.1:8501>。本目录仅需 `streamlit` 与 `pandas`。

## 页面分区与组件

| 区域 | 组件 | 类别 | 作用 |
| --- | --- | --- | --- |
| 指标区 | `st.columns`、`st.metric` ×3 | 容器 + 展示 | 单位总数、已填地址、当前筛选结果 |
| 筛选区 | `st.text_input` | 输入 | 按编码或名称搜索 |
| 筛选区 | `st.checkbox` | 输入/交互 | 只看有地址的单位 |
| 筛选区 | `st.button` | 交互 | 通过回调清空搜索词 |
| 列表区 | `st.dataframe` + `st.column_config` | 展示 | 中文列名、列宽、隐藏行号 |
| 列表区 | `st.download_button` | 交互 | 导出当前筛选结果为 CSV |
| 列表区 | `st.info` | 展示 | 空结果提示 |
| 新增区 | `st.tabs` | 容器 | 列表 / 新增两个页签 |
| 新增区 | `st.form` + `st.form_submit_button` | 容器 + 交互 | 填写期间不重跑，提交时一次处理 |
| 新增区 | `st.error` / `st.success` | 展示 | 校验失败与新增成功 |

容器类共四个：`columns`、`tabs`、`form`、`expander` 中的前三者已使用；`expander` 留给下一章的筛选进阶。

## 数据与状态

假数据字段与接口契约逐字一致：

```python
{"dept_code": "D001", "full_name": "一中队", "address": "一号营区"}
```

- 首次运行把 `SEED_DEPARTMENTS` 复制进 `st.session_state.departments`；
- 新增成功后追加到同一份列表，并写入 `st.session_state["flash_message"]`，再 `st.rerun()`；
- 重跑后先弹出成功提示再渲染表格，避免「表格已画完才写数据」导致新增行当次不显示。

## 自测

```powershell
python verify_app.py
```

用 `streamlit.testing.v1.AppTest` 驱动页面，不打开浏览器。当前 18 项全部通过：

- 初始渲染：标题、3 个指标、12 行表格；
- 搜索「保障」→ 4 行，筛选指标同步；
- 搜索不存在 → 出现 `st.info`，不渲染空表；
- 「只看有地址」→ 11 行；
- 新增 D013 → 13 行，成功提示出现；
- 重复编码 D001 → 错误提示，行数不变；
- 「清空搜索」→ 恢复 13 行。

## 验收对照

| 教材验收项 | 本工程证据 |
| --- | --- |
| 四类组件齐全 | 上表：输入 3、展示 5、交互 3、容器 3 |
| 表格可读 | `column_config` 中文列名、`hide_index=True`、`width="stretch"` |
| 表单可用 | `st.form` 包住三个输入与提交按钮，提交才处理 |
| 筛选可用 | 搜索 + 复选框；空结果显示 `st.info` |
| 案例完整 | 指标、表格、搜索、新增在同一页面运行 |

## 已知限制

- 数据只在会话内，刷新浏览器或重启进程会回到 12 条种子。
- 没有分页、没有权限、没有后端校验；这些在 16-1 之后补。
- 表格列宽按内容自适应，长地址在窄屏会换行。

## 下一章

16-1 把同一页面的 `SEED_DEPARTMENTS` 换成 `GET /departments`，新增改为 `POST /departments`，并处理 401/422 与加载失败。
