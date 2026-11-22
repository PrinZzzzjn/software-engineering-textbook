# 实训 8-1 完成态项目

这是从实训 7-1 的「单位 + 人员」落库工程演进到「加登录认证」的完成态。department 与 personnel 的全部行为保持不变；新增 `users` 表、`app/core/security.py` 与 user 模块，提供注册、登录与当前用户三个接口。账号写入项目根目录的 `duty.db`，重启后仍在；令牌登记在进程内字典 `TOKEN_STORE`，重启后失效，需要重新登录。

## 启动

要求 Python 3.10 及以上。在本目录执行：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

若 PowerShell 不允许激活脚本，可不激活，直接执行 `.\venv\Scripts\python.exe -m pip ...` 与 `.\venv\Scripts\python.exe -m uvicorn ...`。Linux/macOS 使用 `source venv/bin/activate`。

浏览器打开 <http://127.0.0.1:8000/docs>。`GET /health` 返回 `{"status": "healthy"}`；业务路径为 `/departments`、`/personnel` 与 `/users`，不使用版本化前缀。停止服务按 `Ctrl+C`。

## 目录

```text
项目/
├── main.py                  # 创建应用、健康检查、挂三个路由、建表、幂等 seed（含 admin）
├── requirements.txt         # 运行依赖：fastapi、uvicorn、sqlalchemy（本章不新增）
├── .env.example             # 配置变量示例
├── .gitignore               # 排除环境、密钥、SQLite 数据库与缓存
├── README.md
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py      # engine、SessionLocal、Base、get_db（第 6 章）
│   │   └── security.py      # 盐哈希、令牌、get_current_user（本章新增）
│   └── modules/
│       ├── __init__.py
│       ├── department/      # 六文件，7-1 行为不变
│       ├── personnel/       # 六文件，7-1 行为不变
│       └── user/            # 六文件：controller/service/crud/model/schema/param
└── tests/
    └── test_api.py          # 教师验证用；第 12 章才系统讲测试
```

## 数据库与配置

- 数据库地址从环境变量 `DATABASE_URL` 读取，未设置时回落到本目录的 `duty.db`（`sqlite:///./duty.db`）。
- 本章不引入 `python-dotenv`，`.env` 不会被自动加载；需要改库时在启动前设置系统环境变量。
- 启动时 `create_all` 只在缺失时建表：旧 `duty.db` 已有 `departments`、`personnel` 时，会补建 `users`，不清空旧数据。
- `*.db` 与 `*.db-journal` 已被 `.gitignore` 排除，运行数据不进入仓库。
- 删除 `duty.db` 后重启即可回到初始状态：D001/D002、P001/P002 与 `admin`。

## 接口

### 用户与认证

| 方法 | 路径 | 认证 | 成功 | 失败 |
| --- | --- | --- | --- | --- |
| POST | `/users` | 否 | 201，`{id, username, role, is_active}` | 400（用户名重复）、422 |
| POST | `/users/login` | 否 | 200，`{access_token, token_type, user}` | 401（用户名或密码错误）、422 |
| GET | `/users/me` | Bearer | 200，`{id, role}` | 401（未提供令牌或令牌无效） |

- 注册只收 `username` 与 `password`；`role` 由服务端固定为 `normal`，客户端传了也不生效。
- 密码长度 6–128；不足 6 位由请求模型返回 422。
- 登录响应里的 `user` 只含 `id`、`username`、`role`、`is_active`，任何接口都不返回 `password_hash`。
- 后续请求携带 `Authorization: Bearer <access_token>`。

### 单位与人员（7-1 回归）

| 方法 | 路径 | 成功 | 失败 |
| --- | --- | --- | --- |
| GET | `/departments?page=1&page_size=10&full_name=一` | 200，`{items, total}` | 422 |
| POST | `/departments` | 201 | 400（编码重复）、422 |
| GET | `/departments/{dept_code}` | 200 | 404 |
| PUT | `/departments/{dept_code}` | 200 | 404、422 |
| DELETE | `/departments/{dept_code}` | 204，无正文 | 404 |
| GET | `/personnel?page=1&page_size=10&name=张&dept_code=D001` | 200，`{items, total}` | 422 |
| POST | `/personnel` | 201 | 400（证件号重复或单位不存在）、422 |
| GET | `/personnel/{certificate_number}` | 200 | 404 |
| PUT | `/personnel/{certificate_number}` | 200 | 400（单位不存在）、404、422 |
| DELETE | `/personnel/{certificate_number}` | 204，无正文 | 404 |

## 认证实现要点

- 密码存储格式为 `盐$摘要`：`secrets.token_hex(16)` 生成盐，`hashlib.sha256(盐 + 密码)` 生成摘要。相同密码每次注册得到不同字符串，校验时按 `$` 拆回盐与摘要重算。
- 令牌是 `secrets.token_hex(16)` 生成的随机字符串；服务端在 `TOKEN_STORE` 中登记 `token -> user_id`，令牌本身不携带角色。
- `get_current_user` 从 `Authorization: Bearer` 取令牌，查字典得到 `user_id`，再查 `users` 表取 `role`，返回 `{id, role}`。未带令牌、令牌未登记、用户已不存在，都返回 401。
- `TOKEN_STORE` 是进程内字典：服务重启后旧令牌全部失效，账号不受影响。这是本阶段已知行为。
- 启动 seed 幂等写入 `admin / admin123`（`role=admin`），供登录验收与第 9 章账号管理使用；重复启动不会重复写入。

## 教师验证

在实训根目录执行（测试会把数据库指向系统临时目录，不在仓库生成 `duty.db`）：

```powershell
python -m pytest 项目\tests -q
```

`tests/` 覆盖注册 201、重复 400、短密码 422、登录 200 三字段、错误密码 401、`/users/me` 的 401/200 与注销后 401，以及 department、personnel 的 7-1 回归。`tests/` 只用于教师实跑验证，学生本实训不必编写测试；教材第 12 章才正式引入测试。
