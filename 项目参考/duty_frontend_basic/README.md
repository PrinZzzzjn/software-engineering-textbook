# duty_frontend — 值班数据统计系统前端（Streamlit 参考实现）

> **这是基础版（改造前）**，用于课次 21「前端视觉优化」与美化版
> `../duty_frontend/` 做对比。两版功能完全相同，差异只在视觉与页面组织。
> 运行时可复用美化版的虚拟环境：
> `../duty_frontend/.venv/Scripts/python.exe -m streamlit run app.py --server.port 8502`
>
> 定位：专题三「前端界面构建」的**教师参考实现**。学生照此结构完成自己的前端。
> 后端为 `../duty`（FastAPI），本目录只负责界面与前后端联调。

## 1. 目录结构

```
duty_frontend/
├── app.py                 # 入口：登录门禁 + 首页
├── config.py              # 后端地址、分页大小、超时
├── api_client.py          # 统一请求封装（自动注入 Bearer、统一错误）
├── auth.py                # 登录 / 登出 / 页面访问守卫
├── components/
│   └── table.py           # 表格 + 分页（可复用）
├── pages/
│   ├── 1_部门管理.py       # 列表 / 搜索 / 分页 / 新增 / 编辑 / 删除
│   └── 2_数据统计.py       # 指标卡 + 时间分布 + 月度分布
├── requirements.txt
└── README.md
```

`pages/` 下的文件名会自动出现在左侧导航，文件名前缀数字决定顺序。

## 2. 启动方式

### 2.1 启动后端（先启动）

```bash
cd ../duty
python main.py                 # 或 uvicorn main:app --host 0.0.0.0 --port 8000
```

后端默认地址：`http://127.0.0.1:8000`，接口文档：`http://127.0.0.1:8000/docs`

### 2.2 启动前端

```bash
cd duty_frontend

# 建议单独建虚拟环境，避免与后端依赖互相干扰
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

streamlit run app.py
```

浏览器打开 `http://localhost:8501`。

示例数据登录账号：`admin / admin123`（如不存在，可在 duty 目录执行
`python app/scripts/create_admin.py` 创建）。

如果后端不在本机，用环境变量覆盖：

```bash
set DUTY_API_BASE_URL=http://192.168.1.10:8000   # Windows
```

## 3. 页面说明

| 页面 | 内容 | 对应课次 |
|---|---|---|
| 登录页（`app.py`） | 用户名/密码登录，令牌存入 `session_state`，未登录不能进子页面 | 16、19 |
| 首页（`app.py`） | 欢迎信息、后端健康检查、功能导航 | 16 |
| 部门管理（`pages/1_部门管理.py`） | 列表、按名称搜索、排序、分页、新增、编辑、删除 | 17、18、19 |
| 数据统计（`pages/2_数据统计.py`） | 人员/年份选择、4 个指标卡、24 小时折线图、月度柱状图 | 19、20、21 |

## 4. 接口契约说明（重要）

`duty/api说明.md` 部分内容与实际代码不一致，**以 `duty/app` 下的代码为准**：

| 功能 | 文档写法 | 实际代码 |
|---|---|---|
| 部门列表 | `/api/v1/department` | `/api/v1/departments/`（复数、带尾斜杠） |
| 部门排序参数 | `order` | `sort_order` |
| 创建部门 | 不含 `dept_code` | `DepartmentCreate` **要求 `dept_code` 必填** |
| 人员列表排序参数 | `order` | `order`（人员模块确实用 `order`） |
| 站点分布统计 | `/analytics/site-duty-stats` | 不存在；实际是 `/analytics/workstation-duty-yearly`（按工位） |

本参考实现已按实际代码处理，学生照着做不会踩这些坑。

## 5. 教学映射

| 课次 | 本参考实现中的落点 |
|---|---|
| 16 前端开发框架基础 | `app.py` 页面骨架、`st.set_page_config`、表单登录 |
| 17 常用界面组件 | `st.form`、`st.text_input`、`st.number_input`、`st.dataframe`、`st.line_chart`、`st.bar_chart`、`st.metric` |
| 18 前端页面设计 | `pages/` 多页结构、侧边栏自动导航、页面分工 |
| 19 前后端联合调试（一） | `api_client.py` 统一请求、`st.spinner` 加载状态、数据传递 |
| 20 前后端联合调试（二） | `ApiError` 统一错误、401 清登录态、`st.session_state` 会话状态 |
| 21 前端视觉优化 | 指标卡 + 两张图表组成的数据仪表盘；视觉美化留作课次 21 的练习 |
| 22 前端开发综合实践 | 登录 → 部门 CRUD → 数据统计的完整链路 |

## 6. 扩展方向

- **人员 / 工位 / 值班记录页面**：照 `pages/1_部门管理.py` 的结构复制，改接口路径与字段即可。
- **Matplotlib 图表**：本参考实现用 Streamlit 原生图表（依赖少、好教）；课次 21 可增加 Matplotlib 版本作对比。
- **站点维度统计**：用 `/analytics/workstation-duty-yearly?workstation_id=...&year=...`，加一个工位下拉框。
- **令牌刷新**：后端提供 `/auth/refresh`，可在 `api_client` 中做自动续期（当前仅做 401 失败提示）。
- **角色控制**：登录响应含 `user.role`，可按角色隐藏"新增/编辑/删除"入口（后端仍会做权限校验）。

## 7. 常见问题

**页面提示"无法连接后端服务"**
先确认后端已启动，并访问 `http://127.0.0.1:8000/health` 返回 `{"status":"healthy"}`。

**登录提示"用户名或密码错误"**
示例库里的账号可能不是 `admin123`，执行 `cd ../duty && python app/scripts/create_admin.py` 重置。

**统计页没有数据**
示例数据集中在 **2025 年**，年份输入框默认就是 2025；换成其他年份可能没有记录。

**修改页面后不生效**
Streamlit 默认会在文件保存后提示重新运行；也可在页面右上角手动 Rerun。
