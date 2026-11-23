# 实训 8-1 在落库工程上装登录认证

> **B 档口径（2026-11-23）**：课堂必做是注册 → 登录 → 带令牌访问 `/me`；用户列表、改角色与禁用为课后/演示。
本实训从实训 7-1 的「单位 + 人员」落库工程出发，新增 `users` 表、密码盐哈希与进程内令牌，完成注册、登录、取当前用户三个接口。department 与 personnel 的全部行为保持不变。完成态见 `项目/`，学员起点见 `starter/`，实跑证据见 `验证记录.md`。

## 一、实训概览

| 项目 | 内容 |
| --- | --- |
| 对应教材 | 第 8 章 8.1–8.4 与「◆ 实训 8-1」 |
| 起点 | 实训 7-1 完成态：department + personnel + SQLite 落库 |
| 完成态 | 7-1 全部行为 + users 表 + 注册/登录/当前用户 |
| 建议课时 | 4 学时，180 分钟 |
| 难度 | D3 规模 / L4 认知，结论「合理偏紧」 |
| 必做 | users 表、盐哈希、内存令牌、三个接口、admin seed、回归 |
| 选做（课后） | 令牌过期、登出接口、用户名规则、生产级慢哈希 |
| 教师验证 | `python -m pytest 项目\tests -q`，33 项全绿 |
| 运行端口 | 文档与课堂演示用 8000；验证记录使用 8015 |

## 二、教学目标与教材映射

完成本实训后，学生应能：

1. 在既有落库工程中新增一张表，并说清 `create_all` 的建表范围与旧库兼容方式。
2. 用 `hashlib.pbkdf2_hmac` 与随机盐生成 `盐$迭代次数$摘要`，说明为什么数据库不存明文、为什么同一密码两次注册结果不同。
3. 用 `secrets` 生成随机令牌，用进程内字典维护 `token -> user_id`，说出它与无状态签名令牌的取舍。
4. 按六文件体例写出注册、登录、当前用户三个接口，正确使用 201/400/422/401/200。
5. 用 `Depends` 与 `HTTPBearer` 从请求头取出当前用户，理解「认证失败 401、权限不足 403」的分工。
6. 在新增模块的同时完成 department 与 personnel 的回归，保证 7-1 行为不被破坏。

| 教材位置 | 内容 | 本实训落点 |
| --- | --- | --- |
| 8.1 / 代码 8-1-1 | users 表模型 | `app/modules/user/model.py` |
| 8.1 / 代码 8-1-2 | 用户 CRUD | `app/modules/user/crud.py` |
| 8.1 / 8.2 引导 | 建表前导入模型、挂路由 | `main.py` |
| 8.2 / 代码 8-2-1 | 盐哈希与校验 | `app/core/security.py` |
| 8.2 / 代码 8-2-2 | 令牌生成与解析 | `app/core/security.py` 的 `TOKEN_STORE` |
| 8.3 / 代码 8-3-1 | 请求/响应模型 | `app/modules/user/schema.py` |
| 8.3 / 代码 8-3-2 | 注册与登录服务 | `app/modules/user/service.py` |
| 8.3 / 代码 8-3-3 | 注册/登录路由 | `app/modules/user/controller.py` |
| 8.4 / 代码 8-4-1 | 取当前用户依赖 | `security.get_current_user` |
| 8.4 / 代码 8-4-2 | `/users/me` 路由 | `controller.me` |
| 例 8-1 | 注册、登录、/me 全链路 | `验证记录.md` 手工实测 |
| 实训 8-1 步骤 1–6 | 建表、哈希、接口、依赖、验收 | `分步实现指南.md` 阶段 0–6 |
| 8.5 常见错误 | 哈希校验、令牌、表不存在 | 本 README 第十节 |
| 8.7 提交清单 | 源码、说明、运行数据 | 本 README 第十一节 |

## 三、边界与不变量

**必须遵守**

- 路径不加版本化前缀，统一 `include_router(..., prefix="")`；集合路径是 `/users`，不带尾斜杠。
- 认证只用标准库 `hashlib` 与 `secrets`；不引入第三方密码库或签名库。
- 令牌头固定为 `Authorization: Bearer <token>`。
- users 字段：`id` 自增、`username` 唯一、`password_hash`、`role` 默认 `normal`、`is_active` 默认 1。
- 不建 users 与 departments 的外键。
- 注册成功 201；用户名重复 400；密码不足 6 位 422；登录成功 200；错误密码 401；`/users/me` 无令牌或令牌无效 401。
- 登录响应恰好 `{access_token, token_type, user}`；`user` 恰好 `{id, username, role, is_active}`，任何响应都不得出现 `password_hash`。
- 提供幂等的 `admin / admin123` 创建方式，供登录验收与第 9 章使用。
- `main.py` 在 `create_all` 前导入 user 模型，并挂载三个 router。
- department 与 personnel 的字段、路径、状态码、排序、分页过滤行为全部不变。

**本实训不做**

- 不做管理员权限依赖，不做 403；留到 9-1。
- 不做用户列表、修改、禁用、删除、改密。
- 不做令牌过期、刷新、登出接口；列为课后扩展。
- 不把 department/personnel 接口改成必须登录。
- 不写数据库迁移脚本；教学环境允许删库重建。

## 四、课时与难度

| 阶段 | 内容 | 分钟 |
| --- | --- | --- |
| 0 | 读任务书、确认边界与验收 | 10 |
| 1 | 复制起点、建环境、跑通 7-1 | 15 |
| 2 | users 表、CRUD、建表范围 | 30 |
| 3 | 盐哈希、令牌、TOKEN_STORE | 30 |
| 4 | 注册与登录接口 | 40 |
| 5 | `/users/me` 与依赖注入 | 30 |
| 6 | 回归、验收、提交 | 25 |
| 合计 | | **180** |

难度结论为 **D3 / L4，合理偏紧**。规模上学生新增 8 个文件并改写 `main.py`（共触碰 9 个文件）、约 200 行；认知上要同时处理密码安全、令牌生命周期、401 语义和两个旧模块的回归。时间紧在排错：哈希校验、令牌未登记、`users` 表未建这三类问题都不会在启动时报错，只会表现为 401 或 500。若课堂超时，优先保三个接口与回归，把令牌过期、登出留到课后。详细测算见 `难度评分.md`。

## 五、课前准备

**教师**

- 确认 `starter/` 可独立启动，`/departments` 与 `/personnel` 各 2 条 seed 数据。
- 在临时环境跑一遍 `项目/tests`，确认 33 项全绿。
- 准备演示用 8015 端口或临时数据库，避免与课堂 8000 端口冲突。
- 提醒学生：`duty.db` 是运行数据，不提交；提交前删除或加入忽略。

**学生**

- 已独立完成实训 7-1，能解释 `Base`、`SessionLocal`、`get_db`、六文件分工。
- 已读教材 8.1–8.4，知道 `salt$digest` 的拼接顺序与 Bearer 头格式。
- 复制 `starter/` 到自己的实训目录，先跑通旧接口，再动代码。

## 六、实施步骤

| 步骤 | 任务 | 关键动作 | 产出 |
| --- | --- | --- | --- |
| 1 | 确认起点 | 启动服务，`/departments`、`/personnel` 各 200，`/users` 404 | 起点截图 |
| 2 | 建 users 表 | 写 model、crud、param；`main.py` 导入模型；重启后查表 | 表结构与 CRUD |
| 3 | 哈希与令牌 | 写 `security.py` 上半部分；REPL 验证同密不同哈希 | 哈希与令牌函数 |
| 4 | 注册与登录 | 写 schema、service；补 controller 两个路由；改 main 挂路由与 admin seed | 201/400/422/200/401 |
| 5 | 当前用户 | 补 `get_current_user` 与 `/users/me`；验证 401/200 | Bearer 认证闭环 |
| 6 | 回归与提交 | 跑 department/personnel 回归；重启验证；清理运行数据 | 验收记录 |

每一步的代码、检查点与排错见 `分步实现指南.md`。

## 七、完成态文件清单

```text
实训8-1/
├── README.md
├── 分步实现指南.md
├── 验证记录.md
├── 难度评分.md
├── 接缝表.md
├── 学员版差异说明.md
├── starter/
│   ├── 起点说明.md
│   └── （7-1 完成态 24 个文件）
└── 项目/
    ├── main.py
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── README.md
    ├── app/
    │   ├── core/
    │   │   ├── database.py
    │   │   └── security.py
    │   └── modules/
    │       ├── department/       六文件
    │       ├── personnel/        六文件
    │       └── user/             六文件
    └── tests/
        └── test_api.py
```

新增代码集中在 `app/core/security.py`、`app/modules/user/` 与 `main.py` 的装配部分；`app/core/database.py`、department、personnel 原样沿用。

## 八、快速开始与接口

```powershell
cd 项目
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

打开 <http://127.0.0.1:8000/docs>。首次启动会建三张表并写入 D001/D002、P001/P002 与 `admin/admin123`。

| 方法 | 路径 | 认证 | 成功 | 失败 |
| --- | --- | --- | --- | --- |
| POST | `/users` | 否 | 201 `{id, username, role, is_active}` | 400 用户名已存在；422 |
| POST | `/users/login` | 否 | 200 `{access_token, token_type, user}` | 401 用户名或密码错误；422 |
| GET | `/users/me` | Bearer | 200 `{id, role}` | 401 未提供令牌/令牌无效 |
| GET | `/health` | 否 | 200 `{"status":"healthy"}` | — |

登录后把令牌放进请求头：

```powershell
$token = (Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/users/login `
  -ContentType application/json -Body '{"username":"alice","password":"secret123"}').access_token
Invoke-RestMethod http://127.0.0.1:8000/users/me -Headers @{ Authorization = "Bearer $token" }
```

department 与 personnel 的接口、字段、分页过滤与 7-1 完全一致，见 `项目/README.md`。

## 九、验收清单

- [ ] `POST /users` 新用户返回 201，响应无 `password_hash`，`role=normal`。
- [ ] 重复用户名返回 400，detail 为「用户名已存在」。
- [ ] 5 位密码返回 422，detail 指向 `body.password`。
- [ ] 正确密码登录返回 200，顶层恰好三字段，`token_type=bearer`。
- [ ] 登录响应 `user` 恰好四字段，无 `password_hash`。
- [ ] 错误密码与不存在用户都返回 401，不泄露账号是否存在。
- [ ] 不带令牌访问 `/users/me` 返回 401，detail 为「未提供令牌」。
- [ ] 带有效令牌访问 `/users/me` 返回 200，正文恰好 `{id, role}`。
- [ ] 伪造令牌返回 401；从 `TOKEN_STORE` 删除令牌后同样 401。
- [ ] 重启服务后旧令牌 401，但账号仍可重新登录。
- [ ] `admin/admin123` 可登录，`role=admin`；重复启动不产生第二个 admin。
- [ ] 数据库 `password_hash` 形如 `盐$迭代次数$摘要`，明文密码不落库。
- [ ] 禁用账号后，旧令牌访问 `/me` 返回 401。
- [ ] department 列表 200、total=2、固定排序 D001/D002，过滤与 CRUD 不回归。
- [ ] personnel 列表 200、total=2、固定排序 P001/P002，过滤与 CRUD 不回归。
- [ ] Swagger 中出现用户分组；OpenAPI 路径无版本化前缀。
- [ ] 仓库无 `duty.db`、`venv/`、`.env`、`__pycache__/`。

## 十、常见问题与排错

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 启动报 `no such table: users` | `create_all` 前没导入 user 模型 | 在 `main.py` 顶部导入 `user_model` |
| 正确密码也 401 | 哈希拼接顺序或编码不一致；注册与校验不是同一套函数 | 统一用 `get_password_hash`/`verify_password`，固定「盐 + 密码」顺序 |
| 注册 500 且提示 UNIQUE 约束 | 只查了内存或漏了 `get_by_username` | 注册前查库，重复返回 400 |
| 注册响应出现 `password_hash` | 直接返回了 ORM 对象且没有 `response_model` | 路由挂 `UserOut`，不要手写全字段字典 |
| 登录 200 但 `/me` 401 | 令牌没有登记进 `TOKEN_STORE`，或请求头不是 Bearer | 检查 `create_access_token` 与请求头拼写 |
| `/me` 返回 403 而非 401 | 用了默认 `HTTPBearer()`，缺头时框架返回 403 | 用 `HTTPBearer(auto_error=False)`，缺头手动 401 |
| `/me` 返回 500 | 令牌里的 `user_id` 查不到用户，未处理空值 | 查不到也返回 401 |
| 访问 `/users/` 被重定向 | 集合路径多写了尾斜杠 | 统一写 `/users`，不要依赖重定向 |
| 重启后登录态全失效 | `TOKEN_STORE` 是进程内字典 | 本阶段已知行为，重新登录即可 |
| 重启后账号也没了 | 误用内存数据库或删了 `duty.db` | 确认 `DATABASE_URL` 指向文件；不要用 `:memory:` |
| admin 登录 404/401 | seed 没执行或旧库已有同名普通用户 | 确认启动日志与 `_seed_admin`；检查 users 表 |
| 测试在仓库生成 `duty.db` | 测试没有在导入应用前设置 `DATABASE_URL` | 测试文件先设临时库，再导入 `main` |
| Windows 下 `sqlite3.OperationalError: unable to open database file` | 工作目录不可写或路径含特殊字符 | 换到可写目录，检查 `DATABASE_URL` |

## 十一、提交要求

1. `app/`、`main.py`、`requirements.txt`、`.env.example`、`.gitignore`、`README.md` 源码与说明。
2. department、personnel、user 三个模块完整；不得只交 user。
3. 不提交 `venv/`、`duty.db`、`.env`、`__pycache__/`、`.pytest_cache/`。
4. 提交前自查：服务能从空库启动；`admin/admin123` 可登录；三个用户接口状态码符合验收清单；旧接口回归通过。
5. 建议附一页运行记录：启动命令、注册/登录/`/me` 的请求与响应字段（令牌只留长度或前缀，不贴完整值）。

## 十二、课后扩展与后续衔接

**课后扩展（不计入 180 分钟）**

- 令牌过期：把 `TOKEN_STORE[token]` 改为 `(user_id, expires_at)`，`get_current_user` 检查时间并在过期时删除。
- 登出：新增 `POST /users/logout`，从请求头取令牌并 `TOKEN_STORE.pop`，随后 `/me` 应 401。
- 用户名规则：限制字母数字下划线、长度 3–20，并在注册前统一小写。
- 生产级密码存储：提高 PBKDF2 迭代次数，或改用 scrypt、argon2，并把算法标识一起存进 `password_hash`。
- 多进程部署：`uvicorn --workers N` 时每个进程各有一份 `TOKEN_STORE`，需要改用数据库或 Redis 共享。

**与 9-1 的衔接**

9-1 在本实训之上增加管理员权限依赖（403）、用户列表分页、修改角色与禁用账号，并把认证要求逐步回收至 department/personnel 的敏感接口。`app/modules/user/param.py` 已为列表分页预留参数模型，本实训不挂列表路由。
