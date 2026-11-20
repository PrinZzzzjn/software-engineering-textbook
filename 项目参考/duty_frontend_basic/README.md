# duty_frontend_basic — 执勤电子年鉴前端（基础版）

> 定位：「前端界面构建」的**基础版参考实现**。功能与 `duty_frontend` 完全相同，
> 但没有 `ui.py`、没有自定义 CSS 与 Hero 卡片，用于第 19 章"从能用到好看"的对比。

后端为 `../duty-simplified`（FastAPI），本目录只负责界面与前后端联调。

## 1. 目录结构

```
duty_frontend_basic/
├── app.py                 # 入口：登录门禁 + 首页（纯 Streamlit 组件）
├── config.py              # 后端地址、前缀、分页大小、超时
├── api_client.py          # 统一请求封装
├── auth.py                # 登录 / 守卫（基础版，无 ui 依赖）
├── components/
│   └── table.py           # 表格 + 分页（可复用）
├── pages/
│   ├── 1_部门管理.py       # 单位 CRUD
│   ├── 2_数据统计.py       # 指标卡 + 两张图表
│   ├── 3_人员管理.py       # 人员 CRUD
│   ├── 4_哨位管理.py       # 哨位 CRUD
│   └── 5_执勤记录.py       # 执勤记录
├── requirements.txt
└── README.md
```

## 2. 启动方式

### 2.1 启动后端（先启动）

```bash
cd ../duty-simplified
python main.py
```

首次启动会自动建表并写入教学演示数据（admin/admin123、两个单位、两名人员、两个哨位、2026 年执勤记录）。

### 2.2 启动前端

```bash
cd duty_frontend_basic
# 可复用美化版的虚拟环境
../duty_frontend/.venv/Scripts/python.exe -m streamlit run app.py --server.port 8502
```

浏览器打开 `http://localhost:8502`。

## 3. 与美化版的差异（第 19 章对比）

| 维度 | 基础版（本目录） | 美化版（`duty_frontend`） |
|---|---|---|
| 主题模块 | 无 `ui.py` | 有 `ui.py`，统一配色与 CSS |
| 页面标题 | `st.title` | `ui.page_header` / Hero 横幅 |
| 导航卡片 | 无 | 功能卡片 + 渐变横幅 |
| 图表颜色 | 固定色值 | 主题色 `ui.CHART_COLOR` |
| 操作反馈 | `st.success` | `ui.set_flash` + `st.toast` |
| 功能与接口 | 完全相同 | 完全相同 |

## 4. 接口契约

与美化版完全一致，以 `../duty-simplified` 代码为准：

- 集合路径无尾斜杠；列表只返回 `{"items": [...], "total": n}`；无排序参数；
- 登录 `POST /users/login`；健康检查 `GET /health`；
- 四表字段：单位 `dept_code/full_name/address`，人员 `certificate_number/name/dept_code/rank`，
  哨位 `workstation_id/name/dept_code/is_active`，执勤记录 `id/personnel_certificate_number/workstation_id/start_time/end_time/status`；
- 统计只有 `analytics/staff-duty-yearly` 与 `analytics/duty-time-distribution` 两个接口。
