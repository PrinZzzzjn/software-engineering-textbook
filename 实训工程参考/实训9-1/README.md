# 实训 9-1 用户模块：账号管理

本实训从实训 8-1 的「注册 / 登录 / 当前用户」工程出发，新增管理员授权依赖、用户列表分页与用户修改接口，并把 department、personnel 的写操作从公开收回管理员。完成态见 `项目/`，学员起点见 `starter/`，实跑证据见 `验证记录.md`。认证机制不变：仍是 `hashlib` 盐哈希 + 进程内 `TOKEN_STORE`，不引入签名令牌或第三方密码库。

## 一、实训概览

| 项目 | 内容 |
| --- | --- |
| 对应教材 | 第 9 章 9.1–9.4 与「◆ 实训 9-1」 |
| 起点 | 实训 8-1 完成态：users 表 + 盐哈希 + `TOKEN_STORE` + 注册/登录/`me` + department/personnel |
| 完成态 | 8-1 全部行为 + 管理员依赖 + 用户列表分页 + 用户修改/禁用 + 写接口权限回收 |
| 建议课时 | 2 学时，90 分钟 |
| 难度 | D3 规模 / L4 认知，结论「偏紧」 |
| 必做 | `get_current_admin_user`、`GET /users` 分页、`PUT /users/{id}`、department/personnel 写接口回收、回归 |
| 选做（课后） | 修改角色的全部校验、禁用流程（令牌清理/前端）、按角色筛选、删除用户 |
| 教师验证 | `python -m pytest 项目\tests -q`，23 项全绿；uvicorn 8016 权限矩阵实测 |
| 运行端口 | 文档与课堂演示用 8000；验证记录使用 8016 |

## 二、教学目标与教材映射

完成本实训后，学生应能：

1. 区分认证与授权，说明为什么权限检查必须写在后端，而不是只隐藏前端按钮。
2. 在既有 `get_current_user` 之上包一层管理员依赖，让未登录返回 401、普通用户返回 403。
3. 把第 7 章的分页骨架复用到 users 表，返回 `{items, total}`，且输出不含 `password_hash`。
4. 用 `Optional` 与 `Literal` 限定可修改字段，让非法角色与状态在进入业务层前返回 422。
5. 在 service 中按「存在性 404 → 业务规则 400 → 写入」的顺序实现修改，并让被禁用账号无法登录。
6. 把权限依赖挂回 department、personnel 的写接口，并完成 8-1 与 7-1 的回归。

| 教材位置 | 内容 | 本实训落点 |
| --- | --- | --- |
| 9.1 | 授权、角色、最小权限与权限边界表 | 本 README 第三节权限矩阵 |
| 9.2 / 代码 9-2-1 | `get_current_admin_user` | `app/core/security.py` |
| 9.2 / 9.3 | 管理员账号来源、`admin/admin123` | 8-1 已有 `service.create_admin` 与启动 seed，直接复用 |
| 9.3 / 代码 9-3-1 | 分页参数 | `app/modules/user/param.py` |
| 9.3 / 代码 9-3-2 | 分页查询 | `app/modules/user/crud.py` 的 `list_page` |
| 9.3 / 代码 9-3-3 | 用户列表 service | `app/modules/user/service.py` 的 `list_users` |
| 9.3 / 代码 9-3-4 | 列表接口 | `app/modules/user/controller.py` 的 `GET /users` |
| 9.4 / 代码 9-4-1 | `UserUpdate` | `app/modules/user/schema.py` |
| 9.4 / 代码 9-4-2 | 修改用户 service | `app/modules/user/service.py` 的 `update_user` |
| 9.4 / 代码 9-4-3 | 修改接口 | `app/modules/user/controller.py` 的 `PUT /users/{user_id}` |
| 9.4 / 代码 9-4-4 | 禁用后不能登录 | `service.login` 中的 `is_active` 检查 |
| 9.4 / 代码 9-4-5 | 写接口补权限依赖 | department、personnel 的 `controller.py` |
| 例 9-1 | 200/400/404/422 的归属 | `验证记录.md` 与 `分步实现指南.md` 阶段 4 |
| 实训 9-1 步骤 1–5 | 建 admin、列表、修改、禁用、权限回收 | `分步实现指南.md` 阶段 1–5 |
| 9.4 常见错误 | 401/403 混淆、依赖位置、Literal | 本 README 第十节 |

## 三、边界与不变量

**必须遵守**

- 路径不加版本化前缀，统一 `include_router(..., prefix="")`；集合路径是 `/users`、`/departments`、`/personnel`，不带尾斜杠。
- 认证沿用 8-1：`hashlib` 盐哈希 + `TOKEN_STORE` + `Authorization: Bearer <token>`；不引入签名令牌、第三方密码库或签名库。
- 用户列表与修改只给管理员；未登录 401，普通用户 403，管理员 200。
- 注册、登录、`/users/me` 的成功契约与 8-1 完全一致；任何响应都不得出现 `password_hash`。
- department、personnel 的读接口保持公开；写接口（POST/PUT/DELETE）一律管理员。
- 修改用户只允许 `role`（`admin`/`normal`）与 `is_active`（`0`/`1`）；非法值 422，用户不存在 404，管理员禁用自己 400。
- 被禁用账号登录返回 401「账号已禁用」。
- 运行依赖、`.env.example`、`.gitignore` 与 8-1 保持不变。

**权限矩阵（端点 × 身份 → 状态码）**

| 端点 | 匿名 | 普通用户 | 管理员 |
| --- | --- | --- | --- |
| `GET /health` | 200 | 200 | 200 |
| `POST /users` | 201 / 400 / 422 | 201 / 400 / 422 | 201 / 400 / 422 |
| `POST /users/login` | 200 / 401 / 422 | 200 / 401 / 422 | 200 / 401 / 422 |
| `GET /users/me` | 401 | 200 | 200 |
| `GET /users` | 401 | 403 | 200 |
| `PUT /users/{user_id}` | 401 | 403 | 200 / 400 / 404 / 422 |
| `GET /departments` | 200 / 422 | 200 / 422 | 200 / 422 |
| `GET /departments/{dept_code}` | 200 / 404 | 200 / 404 | 200 / 404 |
| `POST /departments` | 401 | 403 | 201 / 400 / 422 |
| `PUT /departments/{dept_code}` | 401 | 403 | 200 / 404 / 422 |
| `DELETE /departments/{dept_code}` | 401 | 403 | 204 / 404 |
| `GET /personnel` | 200 / 422 | 200 / 422 | 200 / 422 |
| `GET /personnel/{certificate_number}` | 200 / 404 | 200 / 404 | 200 / 404 |
| `POST /personnel` | 401 | 403 | 201 / 400 / 422 |
| `PUT /personnel/{certificate_number}` | 401 | 403 | 200 / 400 / 404 / 422 |
| `DELETE /personnel/{certificate_number}` | 401 | 403 | 204 / 404 |

**本实训不做**

- 不做修改角色的完整业务校验（如「不能取消最后一个管理员」「不能修改自己的角色」）；只做教材要求的 `Literal` 取值校验与「不能禁用自己」。
- 不做完整禁用流程（清理该用户已签发令牌、前端禁用提示、禁用审计）；只做「禁用后不能登录」。
- 不做用户删除、改密、按角色筛选、令牌过期、登出。
- 不改 users 表结构，不引入数据库迁移工具。
- 不改变 7-1 的查询与分页行为。

**关于「禁用」的取舍**

教材 `UserUpdate` 使用 `is_active: Optional[Literal[0, 1]]`，未新增 `disabled` 字段；本项目严格沿用该字段与口径，不自造字段。登录时的禁用响应按教材实训验收取 **401「账号已禁用」**；`项目参考/duty-simplified/` 当前快照写的是 403「账号已停用」，属于同一语义的不同状态码，本实训以教材验收口径为准。

**关于权限回收范围的取舍**

教材 9-4-5 只点名 department 的**新增与删除**。本项目把 department 的 PUT 与 personnel 的 POST/PUT/DELETE 一并收回管理员，理由是：写操作的风险同类，只堵两个入口会留下平行越权敞口；读接口仍公开，不影响 7-1 的查询验收。`项目参考/duty-simplified/` 的当前快照中这些写接口仍未挂认证，本章的收紧是 9-1 的有意变更，接缝见 `接缝表.md`。

## 四、课时与难度

| 阶段 | 内容 | 分钟 |
| --- | --- | --- |
| 0 | 读任务书、确认边界与权限矩阵 | 5 |
| 1 | 复制起点、建环境、跑通 8-1 | 10 |
| 2 | `get_current_admin_user` 与 401/403 | 15 |
| 3 | 用户列表：参数、分页查询、字段过滤 | 20 |
| 4 | 修改用户：`Literal`、404、400、422、禁用登录 | 20 |
| 5 | 权限回收：department/personnel 写接口 | 10 |
| 6 | 回归、验收、提交 | 10 |
| 合计 | | **90** |

难度结论为 **D3 / L4，偏紧**。规模上改 8 个文件（其中 7 个有代码变更）、净增约 111 行，没有新文件；认知上要同时处理认证与授权的分工、401/403 的语义、`Literal` 的 422 位置、404/400 的判断顺序，以及「改一个依赖参数就改变旧接口权限」的跨模块影响。时间紧在排错与回归：权限挂错位置、把 403 写成 401、忘记给 personnel 写接口加依赖，都不会在启动时报错。若课堂超时，优先保管理员依赖、列表分页、修改与权限回收，把「修改角色的全部校验」和「禁用流程」留到课后。详细测算见 `难度评分.md`。

## 五、课前准备

**教师**

- 确认 `starter/` 可独立启动，`/departments`、`/personnel` 各 2 条 seed 数据，`/users` 的注册/登录/`me` 可用。
- 在临时环境跑一遍 `项目/tests`，确认 23 项全绿。
- 准备演示用 8016 端口或临时数据库，避免与课堂 8000 端口冲突。
- 准备三个身份：匿名、`alice/secret123`（普通用户）、`admin/admin123`（管理员）。

**学生**

- 已独立完成实训 8-1，能解释 `get_current_user` 如何从 Bearer 令牌取出 `{id, role}`。
- 已读教材 9.1–9.4，知道 401 与 403 的分工、`Literal` 与 `Optional` 的作用。
- 复制 `starter/` 到自己的实训目录，先跑通 8-1 的三个用户接口，再动代码。
- 知道 `admin/admin123` 已由 8-1 启动 seed 写入，不需要另写脚本。

## 六、实施步骤

| 步骤 | 任务 | 关键动作 | 产出 |
| --- | --- | --- | --- |
| 1 | 确认起点 | 启动服务，8-1 的注册/登录/`me` 与旧列表均通过 | 起点截图 |
| 2 | 管理员依赖 | 在 `security.py` 追加 `get_current_admin_user`；用 `/users` 临时验证 401/403 | 401/403 分工 |
| 3 | 用户列表 | 补 `param`、`crud.list_page`、`service.list_users`、`GET /users` | `{items, total}`，无密码哈希 |
| 4 | 修改用户 | 补 `UserUpdate`、`service.update_user`、`PUT /users/{id}`；登录补 `is_active` | 200/400/404/422；禁用登录 401 |
| 5 | 权限回收 | department、personnel 的 POST/PUT/DELETE 挂管理员依赖 | 匿名 401、普通 403、管理员成功 |
| 6 | 回归与提交 | 跑 23 项测试；手工走权限矩阵；清理运行数据 | 验收记录 |

每一步的代码、检查点与排错见 `分步实现指南.md`。

## 七、完成态文件清单

```text
实训9-1/
├── README.md
├── 分步实现指南.md
├── 验证记录.md
├── 难度评分.md
├── 接缝表.md
├── 学员版差异说明.md
├── starter/
│   ├── 起点说明.md
│   └── （8-1 完成态 32 个文件）
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

本实训不新增源码文件，只修改 8 个：`security.py`、user 模块的 `param/crud/service/schema/controller`、department 与 personnel 的 `controller.py`（`param.py` 仅改注释）。`main.py`、`database.py`、三张表模型、运行依赖与配置均不变。

## 八、快速开始与接口

```powershell
cd 项目
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

打开 <http://127.0.0.1:8000/docs>。首次启动会建三张表并写入 D001/D002、P001/P002 与 `admin/admin123`。

```powershell
$base = "http://127.0.0.1:8000"
$admin = (Invoke-RestMethod -Method Post -Uri "$base/users/login" -ContentType "application/json" -Body '{"username":"admin","password":"admin123"}').access_token
$alice = (Invoke-RestMethod -Method Post -Uri "$base/users/login" -ContentType "application/json" -Body '{"username":"alice","password":"secret123"}').access_token

Invoke-RestMethod "$base/users?page=1&page_size=10" -Headers @{ Authorization = "Bearer $admin" }
try { Invoke-RestMethod "$base/users" -Headers @{ Authorization = "Bearer $alice" } } catch { $_.ErrorDetails.Message }
```

完整端点与状态码见第三节权限矩阵；响应字段与 8-1 的兼容说明见 `项目/README.md`。

## 九、验收清单

- [ ] `GET /users` 匿名 401「未提供令牌」，普通用户 403「权限不足」，管理员 200。
- [ ] `GET /users` 返回 `{items, total}`，条目恰好 `id/username/role/is_active`，响应文本无 `password_hash`。
- [ ] `?page=2&page_size=5` 能翻页；`page=0`、`page_size=0`、`page_size=101`、非整数均 422。
- [ ] `PUT /users/{id}` 匿名 401、普通 403；管理员改角色/状态 200。
- [ ] 目标用户不存在 404「用户不存在」；管理员禁用自己 400「不能禁用自己」。
- [ ] `role="superuser"`、`is_active=2` 均 422，且 `type=literal_error`。
- [ ] 管理员把普通用户 `is_active` 改为 0 后，该用户登录 401「账号已禁用」；改回 1 后登录 200。
- [ ] 普通用户被改成 `admin` 后，旧令牌立刻可访问 `GET /users`（角色从库读）。
- [ ] department 的 POST/PUT/DELETE：匿名 401、普通 403、管理员 201/200/204。
- [ ] personnel 的 POST/PUT/DELETE：匿名 401、普通 403、管理员 201/200/204。
- [ ] department、personnel 的列表与详情仍可匿名访问，分页/过滤/排序与 7-1 一致。
- [ ] 8-1 回归：注册 201、重复 400、短密码 422、登录 200 三字段、错误密码 401、`/me` 401/200。
- [ ] OpenAPI 路径无版本化前缀；集合路径无尾斜杠。
- [ ] 仓库无 `duty.db`、`venv/`、`.env`、`__pycache__/`、`.pytest_cache/`。

## 十、常见问题与排错

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 普通用户访问 `/users` 仍 200 | 依赖没挂，或挂在了函数体里 | 列表用装饰器 `dependencies=[Depends(get_current_admin_user)]` |
| 匿名访问得到 403 而非 401 | 绕过了 `get_current_user`，或用了默认 `HTTPBearer()` | 管理员依赖必须包在 `get_current_user` 之上 |
| 普通用户修改用户仍 200 | 修改接口只写了 `Depends(get_current_user)` | 改为 `Depends(get_current_admin_user)` |
| 列表响应出现 `password_hash` | 直接返回 ORM 对象 | service 中手工组装四项字段 |
| `total` 与 `items` 不符 | `count()` 与取页不是同一个 query | 复用 `crud.list_page` 的同一 query |
| `Literal` 校验不生效 | 请求模型写成了普通 `str` / `int` | 用 `Optional[Literal[...]]`，422 的 `type` 为 `literal_error` |
| 禁用自己仍 200 | 漏了 `current_user["id"] == user_id` | 在 404 之后、更新之前判断 |
| 被禁用账号仍能登录 | `login` 没查 `is_active` | 在签发令牌前补检查，返回 401 |
| 普通用户仍能新增单位 | 依赖挂在函数体而不是路由装饰器 | POST/PUT/DELETE 装饰器都要加 |
| 管理员也被 403 | seed 的 admin 角色不是 `admin`，或登录的不是 admin | 检查 users 表与登录账号 |
| 改角色后仍 403 | `get_current_user` 把角色写死或缓存了 | 每次按 user_id 查库取 `role` |
| 测试在仓库生成 `duty.db` | 导入应用前没设置 `DATABASE_URL` | 测试文件先设临时库，再导入 `main` |

## 十一、提交要求

1. `app/`、`main.py`、`requirements.txt`、`.env.example`、`.gitignore`、`README.md` 源码与说明。
2. department、personnel、user 三个模块完整；不得只交 user。
3. 不提交 `venv/`、`duty.db`、`.env`、`__pycache__/`、`.pytest_cache/`。
4. 提交前自查：匿名/普通/管理员三种身份各走一遍权限矩阵；8-1 与 7-1 回归通过。
5. 建议附一页运行记录：三种身份的状态码表、列表分页结果、修改与禁用结果（令牌只留长度或前缀，不贴完整值）。

## 十二、课后扩展与后续衔接

**课后扩展（不计入 90 分钟）**

- **修改角色的全部校验**：禁止取消最后一个管理员；禁止修改自己的角色；角色变更写审计日志；把这些规则从 controller 移到独立业务函数并补测试。
- **禁用流程**：禁用时按 `user_id` 反向清理 `TOKEN_STORE` 中该用户的全部令牌，让已登录会话立即失效；前端在 401 时提示「账号已禁用」而不是「密码错误」；补启用/禁用审计。
- 给列表补按角色筛选，并说明过滤为什么要放在 `count()` 之前（第 7 章 7.3）。
- 用户删除与改密：删除前检查是否存在业务引用；改密后清理旧令牌。
- 检查所有响应是否都经过输出模型；用 OpenAPI 对照字段。
- **复习任务**：回看第 8 章 8.4（认证依赖）、第 7 章 7.2–7.4（查询骨架）、第 4 章 4.5（`Depends`）、第 3 章 3.5–3.6（Pydantic 与 `HTTPException`），说明认证、授权、输入校验与业务规则各拦住哪一类问题。

**与 10-1 的衔接**

10-1 进入执勤记录（`duty_record`）与业务规则：新增记录表、时间区间校验、人员/哨位存在性校验、状态与统计口径。本实训建立的 `get_current_admin_user` 与权限矩阵可直接复用到新模块；届时需要决定新模块的读接口是否公开、写接口是否继续只给管理员，并把决定写进 10-1 的接缝表。
