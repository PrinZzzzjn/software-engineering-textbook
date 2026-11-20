# 实训 8-1 实训手册：在落库工程上装登录认证

> **对应教材**：第 8 章《用户模块：登录认证》◆ 实训 8-1
> **课次**：课次 8（4 学时 · 实践）｜前置：第 6、7 章的落库工程（含 `duty.db`）；第 3 章 3.5、3.6，第 6 章 6.1
> **交付**：项目仓库、验收记录

## 一、实训概览

| 项目 | 内容 |
| --- | --- |
| 实训编号 | 实训 8-1 |
| 实训名称 | 在落库工程上装登录认证 |
| 对应教材 | 第 8 章 8.1–8.4 |
| 课次与学时 | 课次 8 · 4 学时 · 实践（180 分钟） |
| 组织形式 | 独立完成 |
| 场地与工具 | 可运行 Python 的计算机；已安装 Git；终端；浏览器 |
| 配套文件 | [分步实现指南.md](分步实现指南.md)、[验收记录.md](验收记录.md)、[项目/](项目/) |

本次实训在第 6、7 章的落库工程上继续：沿用 `app/core/database.py` 的 `Base` 与 `get_db`，新建 users 表与用户模块，实现注册、登录与当前用户三个接口。密码只存哈希，受保护接口靠令牌识别身份。账号写入 `duty.db`，重启后仍在；令牌字典 `TOKEN_STORE` 仍在内存里，重启后需重新登录。

## 二、学习目标与验收标志

### 2.1 本课结束后应能做到

| 编号 | 学习目标（能做什么） | 对应第 8 章目标 | 达标要点 |
| --- | --- | --- | --- |
| L1 | 说明认证回答什么问题，以及 401 表示什么 | 1 | 认证确认“你是谁”；401 表示未认证或凭证无效 |
| L2 | 解释用户数据四个核心字段，说明密码为什么只存哈希 | 2 | `username` 不重复、`password_hash` 不可逆、`role`/`is_active` 供第 9 章使用 |
| L3 | 实现注册、登录与 `/me`，走通令牌的签发、携带与校验 | 3 | 201/400/422/200/401 各归其位；`/me` 能返回 `{id, role}` |
| L4 | 用 `Depends` 挂认证依赖，说明两种 401 的来源 | 4 | 未带令牌 → 401；令牌未登记 → 401 |

步骤与目标的对应：步骤 1–2 支撑 L1、L2；步骤 3–4 支撑 L3；步骤 5 支撑 L4；步骤 6 检验全部目标。

### 2.2 验收标志

| 接口 | 方法 | 成功返回 | 失败返回 |
| --- | --- | --- | --- |
| `/api/v1/users` 注册 | POST | 201 + `UserOut`（无 `password_hash`） | 用户名重复 → 400；字段不合法 → 422 |
| `/api/v1/users/login` 登录 | POST | 200 + `{access_token, token_type, user}` | 密码错 → 401 |
| `/api/v1/users/me` 当前用户 | GET | 200 + `{id, role}` | 未带令牌 / 令牌无效 → 401 |

同时要求：`requirements.txt` 含第 6 章加入的 `sqlalchemy`，本章不新增依赖；`users` 表已建立且重启后记录仍在；第 6 章的单位接口仍可用；`duty.db` 不入库；提交一次可读的 Git 记录。

### 2.3 本课知识点与教材位置

| 知识点 | 掌握程度 | 教材位置 |
| --- | --- | --- |
| 用户数据的组织 | 能说出四个核心字段，以及 `User(Base)` 表模型与 `create_all` 的写法 | 8.1 |
| 密码哈希 | 能说明只存哈希的理由，以及哈希与校验必须同方案 | 8.2 |
| 令牌 | 能说明随机令牌的生成、字典登记与校验，以及 Bearer 头写法 | 8.2 |
| 注册与登录 | 能说明查重、哈希、入库与验密码、签发令牌的流程 | 8.3 |
| 认证依赖 | 能用 `Depends` 挂依赖，说明两种 401 | 8.4 |

## 三、本次实训的边界

**本实训不做的**（留给后续章）：

| 不做的事 | 留给哪一章 |
| --- | --- |
| 管理员依赖、用户列表、修改角色与启停 | 第 9 章 |
| 用户详情与按角色筛选 | 第 9 章课后扩展 |
| pytest 自动测试 | 第 12 章 |

判断标准是本章只回答“你是谁”；“你能做什么”属于第 9 章，“数据怎么存”已在第 6 章解决，本章只把 users 表接进同一套基础设施。

## 四、课前准备

### 4.1 知识准备

- [ ] 第 6、7 章的工程可启动，`/health` 与 `/api/v1/departments` 均返回 200，`duty.db` 已生成
- [ ] 读过 8.1–8.4，能说出 `Depends` 的作用（3.6）
- [ ] 知道 Git 的基本提交操作（第 5 章）

### 4.2 环境准备

| 项 | 要求 | 检查方法 |
| --- | --- | --- |
| Python | 3.10 及以上 | `python --version` |
| 第 6、7 章工程 | 可启动，已建 departments 表 | `uvicorn main:app --reload` 后访问 `/health` |
| Git | 已初始化 | `git status` 显示当前分支 |
| 浏览器 | 可访问本机端口 | 打开 `/docs` |

### 4.3 材料准备

1. 在第 6、7 章的工程目录上继续，不要另建空目录。
2. 准备 [验收记录.md](验收记录.md) 的电子副本，按本人学号命名。
3. 复制 `.env.example` 为 `.env`（可选；不复制时使用代码中的占位默认值）。

## 五、时间安排

| 步骤 | 内容 | 分钟 |
| --- | --- | ---: |
| — | 课前检查：5-1 工程启动、Git 状态 | 10 |
| 1 | 依赖与配置 | 15 |
| 2 | users 表与四个字段 | 30 |
| 3 | 密码哈希与令牌 | 30 |
| 4 | 注册与登录 | 40 |
| 5 | 受保护接口 | 30 |
| 6 | 验证与提交 | 25 |
| — | 合计 | 180 |

时间不足时，优先保住步骤 4、5；users 表与 `create_all` 必须最先完成，否则后面全部无法验证。

## 六、操作步骤

每一步给出四项内容：做什么、预期输出、做错会看到什么、本步检查点。完整代码见 [分步实现指南.md](分步实现指南.md) 对应阶段。

### 步骤 1：依赖与配置（15 分钟）

**做什么**

1. 本章不新增第三方依赖：数据库连接用的 `sqlalchemy` 已在第 6 章加入，密码哈希用 `hashlib`，随机盐与令牌用 `secrets`。
2. `requirements.txt` 保持第 6 章的四项（`fastapi`、`uvicorn[standard]`、`pydantic`、`sqlalchemy`），重新执行一次安装确认环境可用。
3. `.env.example` 含 `DEBUG` 与 `DATABASE_URL`；本章不引入签名密钥或外部服务配置。

**预期输出**：`pip list` 四项齐备；`/health` 与单位列表仍为 200。

**做错会看到什么**

- `ModuleNotFoundError: fastapi`：依赖装到了系统 Python，确认 `(venv)` 已激活。
- 端口占用：换端口启动。

**检查点**

- [ ] 四项依赖可用
- [ ] `/health` 200
- [ ] `/api/v1/departments/` 200

### 步骤 2：users 表与四个字段（30 分钟）

**做什么**

1. 第 6 章已建 `app/core/database.py`，其中 `Base` 是表模型父类、`get_db` 把一次请求的会话交给接口。
2. 新建 `app/modules/user/__init__.py` 与 `model.py`，让 `User` 继承 `Base`，声明 `__tablename__ = "users"` 与五个字段（`id` 自增主键、`username` 唯一且非空、`password_hash`、`role`、`is_active`）。
3. 新建 `crud.py`，写 `get_by_username`、`get_by_id`、`list_all`、`create`、`update` 五个函数，签名都带 `db: Session`，用 `db.query(User)` 读写、`db.commit()` 提交、`db.refresh()` 取回自增 id。
4. 更新 `main.py`：在已有的 `Base.metadata.create_all(bind=engine)` 之前补一行 `from app.modules.user import model as user_model`，挂上 user 路由，**保留** department 路由。`create_all` 只识别已导入的模型。

**预期输出**：重启后 `duty.db` 中出现 `users` 表且初始为空；`/docs` 中出现“用户”分组；单位接口仍为 200。

**做错会看到什么**

- `no such table: users`：`main.py` 漏了 user 模型导入，或服务未重启执行 `create_all`。
- `TypeError` 提示缺 `db`：`crud.py` 还是内存版签名。
- 单位接口 404：替换 `main.py` 时删掉了 department 的 `include_router`。

**检查点**

- [ ] `User` 继承 `Base`，`users` 表已建立且初始为空
- [ ] `crud.py` 五个函数都带 `db: Session`
- [ ] 两个模块的路由都出现在 `/docs`
- [ ] 单位列表仍为 200

### 步骤 3：密码哈希与令牌（30 分钟）

**做什么**：新建 `app/core/security.py`，写 `get_password_hash`、`verify_password`、`TOKEN_STORE`、`create_access_token`、`resolve_token`。

**预期输出**：`python -c "from app.core.security import create_access_token; print(create_access_token(1)[:16])"` 输出 16 位随机串。

**做错会看到什么**

- 导入报错：文件名或所在目录写错。
- 校验总是 `False`：注册与登录用的不是同一种哈希格式（应为 `盐$摘要`）。
- 令牌查不到：`create_access_token` 没把令牌登记进 `TOKEN_STORE`。

**检查点**

- [ ] 四个函数可导入
- [ ] 能生成令牌
- [ ] `verify_password` 对同一密码返回 `True`

### 步骤 4：注册与登录（40 分钟）

**做什么**

1. 新建 `schema.py`：`UserCreate`、`UserOut`、`UserLogin`、`TokenOut`；`TokenOut` 嵌套 `UserOut`。
2. 在 `crud.py` 补齐五个函数（`get_by_username` 与 `create` 已在步骤 2 写好）。
3. 新建 `service.py`：`create_user` 调 `crud.get_by_username` 查重、哈希后调 `crud.create`；`login` 调 `crud.get_by_username`、验密码、发令牌。
4. 新建 `controller.py`：注册 201、登录 200 两条路由，签名带 `db: Session = Depends(get_db)` 并传给 service。

**预期输出**：注册 201 且响应无 `password_hash`；重名 400；短密码 422；登录 200 且含 `access_token`、`token_type` 与 `user`；错密码 401。

**做错会看到什么**

- 正确密码也 401：注册存了明文，或哈希与校验用了不同方案。
- 响应出现 `password_hash`：没写 `response_model=UserOut`。
- 登录响应缺 `user`：`TokenOut` 没嵌 `UserOut`，或 `UserOut` 没设 `from_attributes=True`。
- 307：请求地址多了尾斜杠。

**检查点**

- [ ] 注册 201，users 表中 `password_hash` 非明文
- [ ] 重名 400、短密码 422
- [ ] 登录 200 并拿到令牌
- [ ] `crud.py` 中不出现 `HTTPException`
- [ ] 错密码 401

### 步骤 5：受保护接口（30 分钟）

**做什么**

1. 在 `security.py` 追加 `bearer_scheme` 与带 `db: Session = Depends(get_db)` 的 `get_current_user`。
2. 在 `controller.py` 追加 `GET /me`，用 `Depends(get_current_user)`。

**预期输出**：不带令牌 401；带有效令牌 200，返回 `{id, role}`；无效令牌 401。

**做错会看到什么**

- 永远 401：请求头漏了 `Bearer ` 前缀。
- `/me` 500：`resolve_token` 返回 `None` 后仍去查用户表，或 `crud.get_by_id` 未导入。
- 把 403 当 401 用：本章只做认证，403 属于第 9 章。

**检查点**

- [ ] 无令牌 401
- [ ] 有效令牌 200，`id` 为整数
- [ ] 无效令牌 401

### 步骤 6：验证与提交（25 分钟）

**做什么**

1. 重启服务，确认账号仍在、旧令牌已失效（需重新登录），按验收记录逐项验证三个接口与失败分支。
2. 确认单位接口仍为 200。
3. 提交：

```bash
git add -A
git status
git commit -m "feat(users): 注册、登录与受保护接口"
```

**预期输出**：验收记录 7 行全部一致；`git status` 干净；`git ls-files` 中无 `.env`、`venv/`、`duty.db`。

**做错会看到什么**

- 提交漏掉依赖：用了 `git add app/`，改为 `git add -A`。
- 记录只写“成功”：必须写实际状态码与响应要点。

**检查点**

- [ ] 三个接口的成功与失败分支均有记录
- [ ] 单位接口未被破坏
- [ ] 提交可读，工作区干净

## 七、配套项目文件

```text
实训8-1/
├── README.md          本手册
├── 分步实现指南.md     六个阶段的代码、命令与验证（教师演示／自查）
├── 验收记录.md        接口、users 表、依赖与 Git 核对表（学生填写）
└── 项目/              完成后的工程（第 6、7 章落库工程 + users 表），可直接启动
    ├── main.py         导入两个模型并执行 create_all
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── README.md
    └── app/
        ├── __init__.py
        ├── core/
        │   ├── __init__.py
        │   ├── database.py  第 6 章建立：engine、Session、Base、get_db
        │   └── security.py  本章建立：哈希、令牌、认证依赖
        └── modules/
            ├── __init__.py
            ├── department/  第 6 章起为落库版，保持不变
            │   ├── __init__.py
            │   ├── controller.py
            │   ├── service.py
            │   ├── crud.py
            │   ├── model.py
            │   ├── schema.py
            │   └── param.py
            └── user/  本章新增（落库版）
                ├── __init__.py
                ├── model.py
                ├── schema.py
                ├── crud.py
                ├── service.py
                └── controller.py
```

使用方式：在第 6、7 章的工程上按 [分步实现指南.md](分步实现指南.md) 推进；[项目/](项目/) 是完成后的状态，可启动对照，不得原样提交。

## 八、验收标准

| 验收项 | 判定内容 | 权重 |
| --- | --- | ---: |
| 注册与登录闭环 | 注册 201/400/422、登录 200/401 均正确 | 30 |
| 受保护接口 | `/me` 无令牌 401、有效令牌 200、无效令牌 401 | 25 |
| 数据安全 | users 表中 `password_hash` 非明文；响应无 `password_hash` | 20 |
| 依赖与版本记录 | 四项依赖可复现；提交可读；旧接口未破坏 | 25 |

判定尺度：

- **通过**：四项均达到，出口检查五题中至少四题答出。
- **部分通过**：某项缺一到两条，或出口检查三题及以上答不出。限期补齐。
- **不通过**：服务无法启动、注册或登录不可用、users 表中出现明文密码。

提交前自检：

- [ ] 三个接口的成功与失败分支均有实际结果
- [ ] 响应中无 `password_hash`
- [ ] 单位接口仍为 200
- [ ] 提交信息可读

## 九、排错清单

| 现象 | 先查什么 |
| --- | --- |
| `ModuleNotFoundError: fastapi` | 依赖是否装到当前解释器 |
| `ModuleNotFoundError: app.core` | `app/core/__init__.py` 是否创建 |
| `/api/v1/users` 404 | `main.py` 是否 `include_router(user_controller.router, ...)` |
| 单位接口 404 | 替换 `main.py` 时是否保留 department 路由 |
| 重启后账号全部消失 | `model.py` 仍是内存版，或 `create_all` 未执行 | 检查 `User` 是否继承 `Base`、`main.py` 是否导入 user 模型 |
| 正确密码登录也是 401 | 注册时是否哈希；`verify_password` 是否按 `$` 拆分盐与摘要 |
| 刚登录就 401 | 请求头是否为 `Authorization: Bearer <token>`；令牌是否登记进 `TOKEN_STORE`（后端重启会清空） |
| `no such table: users` | `main.py` 是否导入 user 模型并执行 `create_all` |
| 422 `string_too_short` | 看 `detail` 的 `loc`，调整输入或约束 |
| 响应出现 `password_hash` | 是否声明 `response_model=UserOut` |
| 登录响应缺 `user` | `TokenOut` 是否嵌套 `UserOut`；`UserOut` 是否设 `from_attributes=True` |
| 307 重定向 | 请求地址是否多了尾斜杠，写成 `/api/v1/users` |

## 十、提交要求

提交两项：**项目仓库**（含 `.git`）、**验收记录**。

```text
学号-姓名-实训8-1/
├── duty/             项目仓库，含 .git
└── 验收记录.md
```

要求：

1. 仓库须包含第 6 章的单位模块（落库版），不得为本次实训删掉。
2. 不要打包 `venv/`、`.env`、`duty.db`。
3. 验收记录须写实际状态码与响应要点，不接受只写“成功”。

## 十一、课后扩展

- 给令牌加过期时间：把 `TOKEN_STORE` 的值从 `user_id` 改成 `(user_id, 失效时刻)`，`resolve_token` 先比较时间再返回；验证过期后访问 `/me` 得到 401。
- 给注册接口加“用户名只允许字母、数字、下划线”的约束（提示：`Field` 的 `pattern`）。
- **复习任务**：对照第 6 章与本章，指出本章新增了哪些文件、各自解决什么问题；说明 users 表为什么不必改 `database.py`、为什么仍要在 `main.py` 补一行模型导入。

## 十二、下课前的出口检查（10 分钟）

| 题号 | 问题 | 达标要点 | 目标 | 自评 |
| ---: | --- | --- | --- | --- |
| 1 | 认证回答什么问题？401 表示什么？ | 确认“你是谁”；未认证或凭证无效 | L1 | □ 能 □ 需查 □ 不能 |
| 2 | 用户数据哪四个字段是核心？密码为什么只存哈希？ | `username`、`password_hash`、`role`、`is_active`；哈希不可逆，泄露不直接暴露密码 | L2 | □ 能 □ 需查 □ 不能 |
| 3 | 从注册到访问 `/me`，令牌经历了哪三步？ | 登录签发 → 请求头携带 → 服务端校验 | L3 | □ 能 □ 需查 □ 不能 |
| 4 | `get_current_user` 的两种 401 分别由什么触发？ | 未带令牌；令牌无效或过期 | L4 | □ 能 □ 需查 □ 不能 |
| 5 | 与第 6 章相比，本章新增了哪些文件？ | user 五文件、`app/core/security.py`；`database.py` 第 6 章已建 | L2、L4 | □ 能 □ 需查 □ 不能 |

自评说明：**能**＝不看教材可完整回答并举例；**需查**＝能说大意，细节需翻书；**不能**＝答不出。教师在步骤 6 后随机抽两题口头检查。

## 附录 A：常用命令

| 目的 | 命令 |
| --- | --- |
| 安装依赖 | `pip install -r requirements.txt` |
| 启动服务 | `uvicorn main:app --reload` |
| 换端口启动 | `uvicorn main:app --reload --port 8001` |
| 检查哈希函数 | `python -c "from app.core.security import get_password_hash; print(get_password_hash('secret123')[:20])"` |
| 检查令牌函数 | `python -c "from app.core.security import create_access_token; print(create_access_token(1)[:16])"` |
| 查看已跟踪文件 | `git ls-files` |

## 附录 B：预期输出对照

**注册成功（201）**

```json
{"id": 1, "username": "alice", "role": "normal", "is_active": 1}
```

**注册重名（400）**

```json
{"detail": "用户名已存在"}
```

**登录成功（200）**

```json
{"access_token": "9f2c4e1a8b7d3c6f...", "token_type": "bearer", "user": {"id": 1, "username": "alice", "role": "normal", "is_active": 1}}
```

**未带令牌访问 `/me`（401）**

```json
{"detail": "未提供令牌"}
```

**令牌无效（401）**

```json
{"detail": "令牌无效"}
```
