# duty_frontend — 执勤电子年鉴前端（Streamlit 参考实现，美化版）

> 定位：「前端界面构建」的**教师参考实现**。学生照此结构完成自己的前端。
> 后端为 `../duty-simplified`（FastAPI），本目录只负责界面与前后端联调。

## 0. 版本说明（第 19 章对比素材）

| 目录 | 版本 | 用途 |
|---|---|---|
| `duty_frontend/` | **美化版**（当前） | 前端章节正常教学与演示，使用 `ui.py` 统一主题与卡片 |
| `duty_frontend_basic/` | **基础版** | 第 19 章做"从能用到好看"的对比，功能相同、无自定义样式 |

两版功能完全相同，差异只在视觉与页面组织。基础版可直接复用本目录的 `.venv` 运行：
`../duty_frontend/.venv/Scripts/python.exe -m streamlit run app.py --server.port 8502`。

## 1. 目录结构

```
duty_frontend/
├── .streamlit/config.toml # 主题：青绿现代风
├── app.py                 # 入口：登录门禁 + 首页（Hero + 功能卡片）
├── config.py              # 后端地址、前缀、分页大小、超时
├── api_client.py          # 统一请求封装（自动注入 Bearer、统一错误）
├── auth.py                # 登录 / 登出 / 页面访问守卫
├── ui.py                  # 主题色、CSS、Hero、功能卡片、flash 提示
├── components/
│   └── table.py           # 表格 + 分页（可复用）
├── pages/
│   ├── 1_部门管理.py       # 单位 CRUD：列表 / 分页 / 新增 / 编辑删除
│   ├── 2_数据统计.py       # 筛选 + 4 个 KPI + 两张图表卡片
│   ├── 3_人员管理.py       # 人员 CRUD：按单位筛选
│   ├── 4_哨位管理.py       # 哨位 CRUD：启用状态
│   └── 5_执勤记录.py       # 执勤记录：登记 / 筛选 / 删除
├── requirements.txt
└── README.md
```

`pages/` 下的文件名会自动出现在左侧导航，文件名前缀数字决定顺序。

## 2. 启动方式

### 2.1 启动后端（先启动）

```bash
cd ../duty-simplified
python main.py                 # 或 uvicorn main:app --host 0.0.0.0 --port 8000
```

后端默认地址：`http://127.0.0.1:8000`，接口文档：`http://127.0.0.1:8000/docs`。

首次启动时 `main.py` 会自动建表并写入一组教学演示数据：
- 演示账号：`admin / admin123`（role=admin）
- 单位：D001 一中队、D002 二中队
- 人员：P001 张伟（D001）、P002 李娜（D002）
- 哨位：W001 一号哨位（D001）、W002 二号哨位（D002）
- 执勤记录：集中在 2026 年，统计页默认年份即 2026

### 2.2 启动前端

```bash
cd duty_frontend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
streamlit run app.py
```

浏览器打开 `http://localhost:8501`。

如果后端不在本机，用环境变量覆盖：

```bash
set DUTY_API_BASE_URL=http://192.168.1.10:8000   # Windows
```

## 3. 页面说明

| 页面 | 内容 | 对应章节 |
|---|---|---|
| 登录页（`app.py`） | 用户名/密码登录，令牌存入 `session_state`，未登录不能进子页面 | 16、17 |
| 首页（`app.py`） | 欢迎信息、后端健康检查、功能导航 | 16、17 |
| 单位管理（`pages/1_部门管理.py`） | 列表、分页、新增、编辑、删除 | 15、17、18 |
| 数据统计（`pages/2_数据统计.py`） | 人员/年份选择、4 个指标卡、24 小时折线图、月度柱状图 | 19、20 |
| 人员管理（`pages/3_人员管理.py`） | 按单位筛选，证件号/姓名/职级维护 | 15、18 |
| 哨位管理（`pages/4_哨位管理.py`） | 按单位筛选，启用/停用状态维护 | 15、18 |
| 执勤记录（`pages/5_执勤记录.py`） | 登记执勤、按时段冲突规则校验、筛选与删除 | 15、18 |

## 4. 接口契约（以 duty-simplified 代码为准）

| 功能 | 路径 | 说明 |
|---|---|---|
| 健康检查 | `GET /health` | 独立的服务级路由，返回 `{"status":"healthy"}` |
| 登录 | `POST /users/login` | 请求体 `{username, password}`，返回 `{access_token, token_type, user}` |
| 单位 | `/departments` | CRUD；字段 `dept_code`/`full_name`/`address` |
| 人员 | `/personnel` | CRUD；支持 `dept_code` 筛选 |
| 哨位 | `/workstations` | CRUD；字段 `workstation_id`/`name`/`dept_code`/`is_active` |
| 执勤记录 | `/duty-records` | 列表/新增/删除（无更新）；支持人员/哨位筛选 |
| 年度统计 | `GET /analytics/staff-duty-yearly` | 参数 `personnel_certificate_number`、`year` |
| 时段分布 | `GET /analytics/duty-time-distribution` | 参数同上 |

约定：
- 所有集合路径**无尾斜杠**（`/departments` 而非 `/departments/`）；
- 列表只返回 `{"items": [...], "total": n}`，无 `sort_by`/`order` 等排序参数；
- 字段严格对应简化四表 + users，无 `longitude`/`parent_dept_code`/`created_at` 等已砍字段；
- 后端 analytics 只有两个聚合接口，无部门排名 / 贡献度接口，指标卡数据全部来自接口返回。

## 5. 教学映射

| 章节 | 本参考实现中的落点 |
|---|---|
| 14 前端开发框架基础 | `app.py` 页面骨架、`st.set_page_config`、表单登录 |
| 15 常用界面组件 | `st.form`、`st.text_input`、`st.dataframe`、`column_config`、`st.line_chart`、`st.bar_chart`、`st.metric` |
| 17 前端页面设计 | `pages/` 多页结构、侧边栏自动导航、页面分工 |
| 18 数据编辑与页面状态 | CRUD 写操作、`session_state` 分页/筛选、401 清登录态 |
| 19 界面优化与数据可视化 | 指标卡 + 两张图表组成的仪表盘；主题与卡片布局 |
| 20 前端开发综合实践 | 登录 → 单位/人员/哨位/执勤记录 → 数据统计的完整链路 |

## 6. 视觉设计（第 19 章）

- **主题色**：teal-700 `#0F766E`（按钮/链接），页面底色 `#F8FAFC`，卡片白色 `#FFFFFF`，文字 `#0F172A`。配置在 `.streamlit/config.toml`。
- **图表系列色**：teal-600 `#0D9488`，已做对比度校验。
- **布局手法**：卡片化 `st.container(border=True)`；KPI `st.metric(..., border=True, icon=...)`；分区 `st.tabs`；表格 `st.column_config` 中文化；操作反馈 `st.toast`。
- **自定义 CSS 的边界**：只做 Hero 横幅、功能卡片、页面留白，集中在 `ui.py`。

## 7. Docker 部署

顶层 `../docker-compose.yml` 已指向 `./duty-simplified` 后端与 `./duty_frontend` 前端：
`cd .. && docker compose up --build`。
前端容器内用 `DUTY_API_BASE_URL=http://backend:8000` 访问后端（服务名，不是 localhost）。
