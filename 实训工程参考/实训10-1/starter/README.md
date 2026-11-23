# 实训 9-1 完成态项目

本项目从实训 8-1 的「注册 / 登录 / 当前用户」工程演进而来，新增管理员授权依赖、用户列表与修改接口，并把 department、personnel 的写操作收回管理员。账号仍写入项目根目录的 `duty.db`，令牌仍登记在进程内字典 `TOKEN_STORE`，重启后旧令牌失效。

## 启动

要求 Python 3.10 及以上。在本目录执行：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

浏览器打开 <http://127.0.0.1:8000/docs>。业务路径为 `/departments`、`/personnel` 与 `/users`，不使用版本化前缀。`GET /health` 返回 `{"status": "healthy"}`。

## 目录

```text
项目/
├── main.py                  # 应用装配、建表、幂等 seed（含 admin）
├── requirements.txt         # 运行依赖：fastapi、uvicorn、sqlalchemy
├── .env.example
├── .gitignore
├── README.md
├── app/
│   ├── core/
│   │   ├── database.py      # engine、SessionLocal、Base、get_db（第 6 章）
│   │   └── security.py      # PBKDF2 盐哈希、令牌、get_current_user、get_current_admin_user
│   └── modules/
│       ├── department/      # 六文件；写接口挂管理员依赖
│       ├── personnel/       # 六文件；写接口挂管理员依赖
│       └── user/            # 六文件；新增列表与修改
└── tests/
    └── test_api.py          # 教师验证用；第 12 章才系统讲测试
```

## 数据库与配置

- 数据库地址从环境变量 `DATABASE_URL` 读取，未设置时回落到本目录的 `duty.db`。
- 启动时 `create_all` 只在缺失时建表；旧库已有 `departments`、`personnel`、`users` 时不会清空数据。
- 删除 `duty.db` 后重启即可回到初始状态：D001/D002、P001/P002 与 `admin/admin123`。
- `*.db`、`.env`、`venv/`、`__pycache__/` 均已被 `.gitignore` 排除。

## 接口与权限矩阵

| 端点 | 匿名 | 普通用户 | 管理员 |
| --- | --- | --- | --- |
| `GET /health` | 200 | 200 | 200 |
| `POST /users`（注册） | 201 | 201 | 201 |
| `POST /users/login` | 200 / 401 / 422 | 200 / 401 / 422 | 200 / 401 / 422 |
| `GET /users/me` | 401 | 200 | 200 |
| `GET /users` | 401 | 403 | 200 |
| `PUT /users/{user_id}` | 401 | 403 | 200 / 400 / 404 / 422 |
| `GET /departments`、`GET /departments/{code}` | 200 / 404 | 200 / 404 | 200 / 404 |
| `POST /departments` | 401 | 403 | 201 / 400 / 422 |
| `PUT /departments/{code}` | 401 | 403 | 200 / 404 / 422 |
| `DELETE /departments/{code}` | 401 | 403 | 204 / 404 |
| `GET /personnel`、`GET /personnel/{number}` | 200 / 404 | 200 / 404 | 200 / 404 |
| `POST /personnel` | 401 | 403 | 201 / 400 / 422 |
| `PUT /personnel/{number}` | 401 | 403 | 200 / 400 / 404 / 422 |
| `DELETE /personnel/{number}` | 401 | 403 | 204 / 404 |

`GET /users` 的条目只含 `id`、`username`、`role`、`is_active`，响应中不出现 `password_hash`；查询参数为 `page`（默认 1，最小 1）与 `page_size`（默认 10，1–100），响应为 `{items, total}`，按 `id` 升序。

`PUT /users/{user_id}` 只接受两个可选字段：

```json
{"role": "admin", "is_active": 0}
```

`role` 仅 `admin` / `normal`，`is_active` 仅 `0` / `1`；其它取值由 Pydantic 在进入业务层前返回 422。目标用户不存在返回 404；管理员把**自己**的 `is_active` 改为 0 返回 400「不能禁用自己」。

## 权限实现要点

- `get_current_user` 负责认证：缺令牌、令牌未登记、令牌对应的用户已不存在，均返回 401。
- `get_current_admin_user` 在认证之上负责授权：角色不是 `admin` 返回 403「权限不足」。两层依赖让 401 与 403 自然分工。
- 令牌只登记 `token -> user_id`，角色每次从用户表读取，因此改角色后旧令牌立即按新角色生效。
- 列表接口不需要当前用户对象，权限依赖写在路由装饰器的 `dependencies=[...]`；修改接口要比较 `current_user["id"]` 与目标 `user_id`，权限依赖写在函数参数上。
- 登录时先校验用户名与密码，再检查 `is_active`；被禁用账号返回 401「账号已禁用」。

## 权限回收的取舍

- 教材 9-4-5 明确要求给 `/departments` 的**新增与删除**挂管理员依赖。本项目进一步把 **PUT** 与 personnel 的三条写接口一并收回，保证「写操作一律管理员、读操作保持公开」的口径一致，避免留下同类越权敞口。
- `项目参考/duty-simplified/` 的当前快照中，department 与 personnel 仍未挂认证；本章的权限回收是对该快照的**有意收紧**，以上表为准。
- 读接口（两个列表与详情）保持公开，普通执勤人员不需要登录即可查看。
- 被禁用账号不能重新登录，但禁用前已签发的令牌在服务重启前仍然有效。本章只实现教材要求的「禁用后不能登录」，令牌清理列为课后扩展。

## 与 8-1 的兼容

- 注册 201、重复用户名 400、短密码 422、登录 200 三字段、错误密码 401、`/users/me` 的 401/200 均保持不变。
- department 与 personnel 的路径、字段、分页、过滤、排序、400/404/422 文案均保持不变；唯一变化是写操作新增 401/403。
- 运行依赖、`.env.example`、`.gitignore` 与 8-1 完全相同。

## 教师验证

在实训根目录执行（测试会把数据库指向系统临时目录，不在仓库生成 `duty.db`）：

```powershell
python -m pytest 项目\tests -q
```

`tests/test_api.py` 覆盖：匿名 401 / 普通用户 403 / 管理员 200；用户列表分页、固定排序与字段过滤；修改用户 200/400/404/422；禁用后登录 401；department 与 personnel 写操作的 401/403/201/200/204；读接口公开；8-1 注册/登录/`me` 回归；7-1 查询回归。详细实测见 `../验证记录.md`。
