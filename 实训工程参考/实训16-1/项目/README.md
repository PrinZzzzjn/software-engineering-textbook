# 实训 16-1 完成态项目：数据读取与展示

本项目把 15-1 的单页单位管理从假数据接到真实后端：登录拿令牌，`GET /departments` 读列表，`POST /departments` 新增，并补齐加载、空、错误三种状态。请求逻辑收进 `api_client.py`，页面里不再出现完整 URL。

## 文件

```text
项目/
├── app.py             # 登录门禁 + 列表 + 新增 + 三态
├── config.py          # 基地址、前缀、超时、分页大小
├── api_client.py      # ApiError、_request、get/post/put/delete
├── verify_app.py      # 真后端 + AppTest 联调自测
├── 联调排错记录.md     # 404 / 401 / 422 三次按顺序定位的记录
├── requirements.txt
└── README.md
```

## 运行

先启动后端（实训 13-1 项目，另一个终端）：

```powershell
cd ..\..\实训13-1\项目
python -m uvicorn main:app --port 8000
```

再启动前端：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

前端默认 <http://127.0.0.1:8501>，后端 <http://127.0.0.1:8000>。演示账号 `admin / admin123`。

## 请求封装：四个统一

| 统一项 | 落点 | 作用 |
| --- | --- | --- |
| 地址 | `config.API_BASE_URL` + `api_client._url` | 改端口只改一处 |
| 请求头 | `api_client._headers` | 自动带 `Authorization: Bearer <token>` |
| 超时 | `config.REQUEST_TIMEOUT` | 避免请求无限挂起 |
| 错误 | `api_client.ApiError` | 页面只捕获一种异常 |

401 在 `_request` 里统一处理：清除 `access_token` 并抛出 `ApiError(401, "登录已过期，请重新登录")`；页面收到 401 后写一条提示并重跑，回到登录页。

422 的 `detail` 是列表，`_request` 会把每条 `msg` 用「；」拼成一句话，页面直接显示，不会出现 Python 字典。

## 三种状态

| 状态 | 触发 | 界面 | 代码位置 |
| --- | --- | --- | --- |
| 加载态 | 请求进行中 | `st.spinner("正在加载单位列表...")` | 列表请求外层 |
| 空态 | 请求成功但 `items` 为空 | `st.info("没有符合条件的单位...")` | 列表页签 |
| 错误态 | 连不上、401、404、400、422 | `st.error(exc.detail)` + `st.stop()` | 列表请求 `except` |

401 是特例：先写 `login_notice` 再 `st.rerun()`，重跑后登录页用 `st.warning` 显示「登录已过期」。

## 页面结构

- 登录门禁：没有 `access_token` 时只渲染登录表单，并 `st.stop()`；
- 侧边栏：当前用户、角色、后端健康检查、退出登录；
- 指标：当前条件下的单位数（接口 `total`）、本页显示条数；
- 搜索：按名称把 `full_name` 作为查询参数传给后端；
- 列表页签：`st.dataframe` + `column_config`，空数据显示 `st.info`；
- 新增页签：`st.form` + `POST /departments`，成功提示后重跑刷新列表。

## 自测

```powershell
python verify_app.py
```

脚本要求后端已启动，并用 `AppTest` 驱动页面。覆盖：健康检查、登录页、错误密码、登录成功、种子 2 行、空态（搜索不存在的名称）、清空搜索、新增成功、重复编码 400、超长字段 422、错误前缀 404、令牌失效 401、清理测试单位。

> 脚本只新增/删除测试单位 `D900`、`D902`，不改动 `D001`、`D002` 两条种子数据。

## 验收对照

| 教材验收项 | 本工程证据 |
| --- | --- |
| 接口调用正确 | 四要素与 13-1 `/docs` 一致；路径无版本前缀 |
| 客户端统一 | `config.py` + `api_client.py`；页面只调 `api.get/post` |
| 登录闭环 | 登录失败可读提示；401 清令牌回登录页 |
| 三态齐全 | spinner / info / error + stop；401 特例回登录 |
| 排错有据 | `联调排错记录.md` 三次实验 |

## 已知限制

- 只显示第 1 页（每页 10 条），翻页留到 17-1；
- 搜索只按单位名称（后端 `full_name` 参数），不搜编码与地址；
- 没有编辑、删除，留到 18-1；
- 令牌存 `session_state`，刷新浏览器即失效，需要重新登录；
- 后端种子只有 D001、D002 两条单位，新增数据写在临时库中。

## 下一章

17-1 把单页拆成多页：`pages/` 导航、`auth.require_login`、可复用表格与分页组件；`api_client.py` 原样复用。
