# 实训 6-1 实训手册：给工程装上登录认证

> **对应教材**：第 6 章《用户模块：登录认证》◆ 实训 6-1  
> **课次**：课次 7（4 学时 · 实践）｜前置：第 5 章实训 5-1 的最小工程；第 3 章 3.5、3.6  
> **交付**：项目仓库、验收记录

## 一、实训概览

| 项目 | 内容 |
| --- | --- |
| 实训编号 | 实训 6-1 |
| 实训名称 | 给工程装上登录认证 |
| 对应教材 | 第 6 章 6.1–6.5 |
| 课次与学时 | 课次 7 · 4 学时 · 实践（180 分钟） |
| 组织形式 | 独立完成 |
| 场地与工具 | 可运行 Python 的计算机；已安装 Git；终端；浏览器 |
| 配套文件 | [分步实现指南.md](分步实现指南.md)、[验收记录.md](验收记录.md)、[项目/](项目/) |

本次实训从 5-1 的最小工程继续：保留单位模块，加入 `app/core/` 与用户模块，实现注册、登录与当前用户三个接口。数据从内存搬到 SQLite，密码只存哈希，受保护接口靠令牌识别身份。

## 二、学习目标与验收标志

### 2.1 本课结束后应能做到

| 编号 | 学习目标（能做什么） | 对应第 6 章目标 | 达标要点 |
| --- | --- | --- | --- |
| L1 | 说明认证回答什么问题，以及 401 表示什么 | 1 | 认证确认“你是谁”；401 表示未认证或凭证无效 |
| L2 | 解释用户表四个核心字段，说明密码为什么只存哈希 | 2 | `username` 唯一、`password_hash` 不可逆、`role`/`is_active` 供第 7 章使用 |
| L3 | 实现注册、登录与 `/me`，走通令牌的签发、携带与校验 | 3 | 201/400/422/200/401 各归其位；`/me` 能返回 `{id, role}` |
| L4 | 用 `Depends` 挂认证依赖，说明两种 401 的来源 | 4 | 未带令牌 → 401；令牌无效或过期 → 401 |

步骤与目标的对应：步骤 1–2 支撑 L1、L2；步骤 3–4 支撑 L3；步骤 5 支撑 L4；步骤 6 检验全部目标。

### 2.2 验收标志

| 接口 | 方法 | 成功返回 | 失败返回 |
| --- | --- | --- | --- |
| `/api/v1/users` 注册 | POST | 201 + `UserOut`（无 `password_hash`） | 用户名重复 → 400；字段不合法 → 422 |
| `/api/v1/users/login` 登录 | POST | 200 + `{access_token, token_type}` | 密码错 → 401 |
| `/api/v1/users/me` 当前用户 | GET | 200 + `{id, role}` | 未带令牌 / 令牌无效 → 401 |

同时要求：依赖与配置已更新；`users` 表已建立；第 5 章的单位接口仍可用；提交一次可读的 Git 记录。

### 2.3 本课知识点与教材位置

| 知识点 | 掌握程度 | 教材位置 |
| --- | --- | --- |
| 数据库基础设施 | 能说明 engine、session、`Base`、`get_db` 各管什么 | 6.1 |
| 用户表与约束 | 能说明四个核心字段与唯一、必填约束 | 6.2 |
| 密码哈希 | 能说明只存哈希的理由，以及哈希与校验必须同方案 | 6.3 |
| 令牌 | 能说明载荷、过期、签名与 Bearer 头写法 | 6.3 |
| 认证依赖 | 能用 `Depends` 挂依赖，说明两种 401 | 6.5 |

## 三、本次实训的边界

**本实训不做的**（留给后续章）：

| 不做的事 | 留给哪一章 |
| --- | --- |
| 管理员依赖、用户列表、修改角色与启停 | 第 7 章 |
| 刷新令牌、注册审核、密码重置 | 课程不涉及 |
| 分页与用户详情 | 第 8、9 章 |
| pytest 自动测试 | 第 12 章 |

判断标准是本章只回答“你是谁”；“你能做什么”属于第 7 章。

## 四、课前准备

### 4.1 知识准备

- [ ] 第 5 章的工程可启动，`/health` 与 `/api/v1/departments/` 均返回 200
- [ ] 读过 6.1–6.5，能说出 `Depends` 的作用（3.6）
- [ ] 知道 Git 的基本提交操作（第 5 章）

### 4.2 环境准备

| 项 | 要求 | 检查方法 |
| --- | --- | --- |
| Python | 3.10 及以上 | `python --version` |
| 第 5 章工程 | 可启动 | `uvicorn main:app --reload` 后访问 `/health` |
| Git | 已初始化 | `git status` 显示当前分支 |
| 浏览器 | 可访问本机端口 | 打开 `/docs` |

### 4.3 材料准备

1. 在第 5 章的工程目录上继续，不要另建空目录。
2. 准备 [验收记录.md](验收记录.md) 的电子副本，按本人学号命名。
3. 复制 `.env.example` 为 `.env`（可选；不复制时使用代码中的占位默认值）。

## 五、时间安排

| 步骤 | 内容 | 分钟 |
| --- | --- | ---: |
| — | 课前检查：5-1 工程启动、Git 状态 | 10 |
| 1 | 依赖与配置 | 15 |
| 2 | 数据库基础设施与用户表 | 30 |
| 3 | 密码哈希与令牌 | 30 |
| 4 | 注册与登录 | 40 |
| 5 | 受保护接口 | 30 |
| 6 | 验证与提交 | 25 |
| — | 合计 | 180 |

时间不足时，优先保住步骤 4、5；数据库与依赖必须最先完成，否则后面全部无法验证。

## 六、操作步骤

每一步给出四项内容：做什么、预期输出、做错会看到什么、本步检查点。完整代码见 [分步实现指南.md](分步实现指南.md) 对应阶段。

### 步骤 1：依赖与配置（15 分钟）

**做什么**

1. 在 `requirements.txt` 追加 `sqlalchemy`、`python-jose[cryptography]`、`passlib`、`python-dotenv`。
2. 激活虚拟环境后安装。
3. 复制 `.env.example` 为 `.env`（可选）。

**预期输出**：`pip list` 可见 7 项依赖；`/health` 与单位列表仍为 200。

**做错会看到什么**

- `ModuleNotFoundError: No module named 'jose'`：依赖装到了系统 Python，确认 `(venv)` 已激活。
- 端口占用：换端口启动。

**检查点**

- [ ] 7 项依赖安装成功
- [ ] `/health` 200
- [ ] `/api/v1/departments/` 200

### 步骤 2：数据库基础设施与用户表（30 分钟）

**做什么**

1. 新建 `app/core/__init__.py` 与 `app/core/database.py`（引擎、会话工厂、`Base`、`get_db`）。
2. 按教材 6.1 的对照表，把 dept 的 `model.py` 与 `crud.py` 换成数据库版；`service.py` 与 `controller.py` 只增加 `db` 参数。
3. 新建 `app/modules/user/__init__.py` 与 `model.py`，定义 `User`。
4. 更新 `main.py`：导入 `Base`、`engine`、dept 与 user 的模型，挂上 dept 与 user 路由，最后调用 `create_all`。

**预期输出**：项目根目录出现 `duty.db`；`/docs` 中出现“用户”分组；单位接口仍为 200。

**做错会看到什么**

- `ModuleNotFoundError: app.core`：`__init__.py` 没建。
- 单位接口 404：替换 `main.py` 时删掉了 dept 的 `include_router`。
- `users` 表不存在：没导入 `model` 或没执行 `create_all`。

**检查点**

- [ ] `duty.db` 已生成
- [ ] 两个模块的路由都出现在 `/docs`
- [ ] 单位列表仍为 200

### 步骤 3：密码哈希与令牌（30 分钟）

**做什么**：新建 `app/core/security.py`，写配置、`get_password_hash`、`verify_password`、`create_access_token`、`decode_token`。

**预期输出**：`python -c "from app.core.security import create_access_token; print(create_access_token({'sub': '1'})[:20])"` 能输出令牌片段。

**做错会看到什么**

- 导入报错：依赖未装或文件名写错。
- 令牌无法解析：签发与解析的 `SECRET_KEY` 或算法不一致。

**检查点**

- [ ] 四个函数可导入
- [ ] 能生成令牌

### 步骤 4：注册与登录（40 分钟）

**做什么**

1. 新建 `schema.py`：`UserCreate`、`UserOut`、`LoginIn`、`TokenOut`。
2. 新建 `crud.py`：`get_by_username` 与 `create`，只取用户与写入，不判断规则。
3. 新建 `service.py`：`create_user` 调 `crud.get_by_username` 查重、哈希后调 `crud.create`；`login` 调 `crud.get_by_username`、验密码、发令牌。
4. 新建 `controller.py`：注册 201、登录 200 两条路由。

**预期输出**：注册 201 且响应无 `password_hash`；重名 400；短密码 422；登录 200 且含 `access_token`；错密码 401。

**做错会看到什么**

- 注册 500：表未建或漏写 `Depends(get_db)`。
- 正确密码也 401：注册存了明文，或哈希与校验用了不同方案。
- 响应出现 `password_hash`：没写 `response_model=UserOut`。
- 307：请求地址多了尾斜杠。

**检查点**

- [ ] 注册 201，库中 `password_hash` 非明文
- [ ] 重名 400、短密码 422
- [ ] 登录 200 并拿到令牌
- [ ] `crud.py` 中不出现 `HTTPException`
- [ ] 错密码 401

### 步骤 5：受保护接口（30 分钟）

**做什么**

1. 在 `security.py` 追加 `bearer_scheme` 与 `get_current_user`。
2. 在 `controller.py` 追加 `GET /me`，用 `Depends(get_current_user)`。

**预期输出**：不带令牌 401；带有效令牌 200，返回 `{id, role}`；无效令牌 401。

**做错会看到什么**

- 永远 401：请求头漏了 `Bearer ` 前缀。
- `/me` 500：`sub` 未转 `int`，或载荷里没有 `sub`。
- 把 403 当 401 用：本章只做认证，403 属于第 7 章。

**检查点**

- [ ] 无令牌 401
- [ ] 有效令牌 200，`id` 为整数
- [ ] 无效令牌 401

### 步骤 6：验证与提交（25 分钟）

**做什么**

1. 重启服务，按验收记录逐项验证三个接口与失败分支。
2. 确认单位接口仍为 200。
3. 提交：

```bash
git add -A
git status
git commit -m "feat(users): 注册、登录与受保护接口"
```

**预期输出**：验收记录 7 行全部一致；`git status` 干净；`git ls-files` 中无 `duty.db`、`.env`、`venv/`。

**做错会看到什么**

- `duty.db` 进了提交：`.gitignore` 的 `*.db` 未生效，`git rm --cached duty.db` 后提交。
- 提交漏掉依赖：用了 `git add app/`，改为 `git add -A`。
- 记录只写“成功”：必须写实际状态码与响应要点。

**检查点**

- [ ] 三个接口的成功与失败分支均有记录
- [ ] 单位接口未被破坏
- [ ] 提交可读，工作区干净

## 七、配套项目文件

```text
实训6-1/
├── README.md          本手册
├── 分步实现指南.md     六个阶段的代码、命令与验证（教师演示／自查）
├── 验收记录.md        接口、数据库、依赖与 Git 核对表（学生填写）
└── 项目/              完成后的工程（5-1 + 用户模块），可直接启动
    ├── main.py
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── README.md
    └── app/
        ├── __init__.py
        ├── core/
        │   ├── __init__.py
        │   ├── database.py
        │   └── security.py
        └── modules/
            ├── __init__.py
            ├── dept/
            │   ├── __init__.py
            │   ├── controller.py
            │   ├── service.py
            │   ├── crud.py
            │   ├── model.py
            │   ├── schema.py
            │   └── param.py
            └── user/
                ├── __init__.py
                ├── model.py
                ├── schema.py
                ├── crud.py
                ├── service.py
                └── controller.py
```

使用方式：在 5-1 的工程上按 [分步实现指南.md](分步实现指南.md) 推进；[项目/](项目/) 是完成后的状态，可启动对照，不得原样提交。

## 八、验收标准

| 验收项 | 判定内容 | 权重 |
| --- | --- | ---: |
| 注册与登录闭环 | 注册 201/400/422、登录 200/401 均正确 | 30 |
| 受保护接口 | `/me` 无令牌 401、有效令牌 200、无效令牌 401 | 25 |
| 数据安全 | 库中 `password_hash` 非明文；响应无 `password_hash` | 20 |
| 依赖与版本记录 | 7 项依赖可复现；提交可读；旧接口未破坏 | 25 |

判定尺度：

- **通过**：四项均达到，出口检查五题中至少四题答出。
- **部分通过**：某项缺一到两条，或出口检查三题及以上答不出。限期补齐。
- **不通过**：服务无法启动、注册或登录不可用、库中出现明文密码。

提交前自检：

- [ ] 三个接口的成功与失败分支均有实际结果
- [ ] `duty.db` 未被 Git 跟踪
- [ ] 响应中无 `password_hash`
- [ ] 单位接口仍为 200
- [ ] 提交信息可读

## 九、排错清单

| 现象 | 先查什么 |
| --- | --- |
| `ModuleNotFoundError: No module named 'jose'` | 依赖是否装到当前解释器 |
| `ModuleNotFoundError: app.core` | `app/core/__init__.py` 是否创建 |
| `/api/v1/users` 404 | `main.py` 是否 `include_router(user_controller.router, ...)` |
| 单位接口 404 | 替换 `main.py` 时是否保留 dept 路由 |
| `no such table: users` | 是否导入模型并执行 `create_all` |
| 正确密码登录也是 401 | 注册时是否哈希；两处是否同用一个 `pwd_context` |
| 刚登录就 401 | 请求头是否为 `Authorization: Bearer <token>`；签发与解析是否同一 `SECRET_KEY` |
| 422 `string_too_short` | 看 `detail` 的 `loc`，调整输入或约束 |
| 响应出现 `password_hash` | 是否声明 `response_model=UserOut` |
| 307 重定向 | 请求地址是否多了尾斜杠，写成 `/api/v1/users` |

## 十、提交要求

提交两项：**项目仓库**（含 `.git`）、**验收记录**。

```text
学号-姓名-实训6-1/
├── duty/             项目仓库，含 .git
└── 验收记录.md
```

要求：

1. 仓库须包含第 5 章的单位模块，不得为本次实训删掉。
2. 不要打包 `venv/`、`.env`、`duty.db`。
3. 验收记录须写实际状态码与响应要点，不接受只写“成功”。

## 十一、课后扩展

- 把 `ACCESS_TOKEN_EXPIRE_MINUTES` 改成 1，等一分钟后再访问 `/me`，观察 401。
- 给注册接口加“用户名只允许字母、数字、下划线”的约束（提示：`Field` 的 `pattern`）。
- **复习任务**：对照第 5 章与本章，指出新增了哪些文件、各自解决什么问题；说明 `app/core/` 为什么此时才出现。

## 十二、下课前的出口检查（10 分钟）

| 题号 | 问题 | 达标要点 | 目标 | 自评 |
| ---: | --- | --- | --- | --- |
| 1 | 认证回答什么问题？401 表示什么？ | 确认“你是谁”；未认证或凭证无效 | L1 | □ 能 □ 需查 □ 不能 |
| 2 | 用户表哪四个字段是核心？密码为什么只存哈希？ | `username`、`password_hash`、`role`、`is_active`；哈希不可逆，泄露不直接暴露密码 | L2 | □ 能 □ 需查 □ 不能 |
| 3 | 从注册到访问 `/me`，令牌经历了哪三步？ | 登录签发 → 请求头携带 → 服务端校验 | L3 | □ 能 □ 需查 □ 不能 |
| 4 | `get_current_user` 的两种 401 分别由什么触发？ | 未带令牌；令牌无效或过期 | L4 | □ 能 □ 需查 □ 不能 |
| 5 | 与第 5 章相比，本章新增了哪些文件与依赖？为什么现在才加？ | `app/core/`、user 四文件、4 项依赖；第一次需要持久化与认证 | L2、L4 | □ 能 □ 需查 □ 不能 |

自评说明：**能**＝不看教材可完整回答并举例；**需查**＝能说大意，细节需翻书；**不能**＝答不出。教师在步骤 6 后随机抽两题口头检查。

## 附录 A：常用命令

| 目的 | 命令 |
| --- | --- |
| 安装依赖 | `pip install -r requirements.txt` |
| 启动服务 | `uvicorn main:app --reload` |
| 换端口启动 | `uvicorn main:app --reload --port 8001` |
| 检查哈希函数 | `python -c "from app.core.security import get_password_hash; print(get_password_hash('secret123')[:20])"` |
| 检查令牌函数 | `python -c "from app.core.security import create_access_token; print(create_access_token({'sub':'1'})[:20])"` |
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
{"access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer"}
```

**未带令牌访问 `/me`（401）**

```json
{"detail": "未提供令牌"}
```

**令牌无效或过期（401）**

```json
{"detail": "令牌无效或已过期"}
```
