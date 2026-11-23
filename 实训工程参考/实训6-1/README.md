# 实训 6-1：数据模块：增删查改（教师用工程参考）

> 对应教材：第 6 章 6.1–6.4 与章末「◆ 实训 6-1」  
> 学时：4 学时，共 180 分钟  
> 示例对象：单位（`department`）  
> 交付：SQLite 数据库版工程、九条接口验证记录、重启持久化证据

本目录是教师完整版，包含完成态、学员起点与真实实跑记录，不直接作为学生提交模板。学生从 `starter/`（5-1 完成态）出发，把内存列表替换为 SQLite 表；六文件的职责与接口契约不变。

## 一、概览

| 项目 | 内容 |
| --- | --- |
| 主目标 1 | 推导数据为什么要落库，说明 `engine`、`Session`、`Base`、`get_db` 各管什么，并在 `main.py` 完成建表 |
| 主目标 2 | 用 department 走通增删查改与分页，返回 `{items, total}`，错误码按层分工 |
| 综合验证 | 新增记录后重启服务仍在；九条测试清单全部可复现 |
| 数据方式 | SQLite 文件 `duty.db`，`DATABASE_URL` 可覆盖；服务启动时建表并幂等 seed |
| 完成态入口 | `项目/main.py` |
| 学员起点 | `starter/起点说明.md` 与 5-1 完成态工程 |
| 教师验证 | 实训根目录执行 `pytest 项目\tests -q`，测试使用临时数据库 |
| 难度初评 | D4 / L4 / 重（依据与拆分建议见 `难度评分.md`） |

本实训不新建业务模块，也不建 `users` 表。课堂增量是「存储替换 + 分页」，不是重写一遍六文件。身份与权限分别到第 8、9 章再加入。

## 二、目标

完成本实训后，学生应能：

1. 说明数据为什么要落库，以及 `engine`、`Session`、`Base`、`get_db` 各自解决什么问题。
2. 说明 `departments` 表怎样建立，主键、必填与长度约束怎样在写入时生效。
3. 按 controller / service / crud / model / schema / param 的调用关系，实现单位新增、详情、修改与删除。
4. 用 `page`、`page_size` 换算出 `offset`、`limit`，实现分页并返回 `items` 与 `total`；固定按 `dept_code` 升序。
5. 按「谁产生、谁负责」区分 422、400、404、500，并验证删除 204 无正文、重复删除 404。
6. 用真实重启证明数据已持久化，并说明内存版与数据库版的行为差异。

### 教材映射表

| 教材位置 | 教材内容 | 工程参考落点 | 验收点 |
| --- | --- | --- | --- |
| 6.1 代码 6-1-1 | `app/core/database.py` 四个角色 | `项目/app/core/database.py` | `engine`、`SessionLocal`、`Base`、`get_db` 齐备；`get_db` 在 `finally` 关闭 |
| 6.1 代码 6-1-2 | `main.py` 建表三行 | `项目/main.py` | 导入模型后执行 `Base.metadata.create_all(bind=engine)`，`duty.db` 出现 |
| 6.2 表结构 | departments 三字段与约束 | `项目/app/modules/department/model.py` | `dept_code` 主键、`full_name` 必填、`address` 可空，长度 20/100/500 |
| 6.2 代码 6-2-2 | 输入与输出模型 | `项目/app/modules/department/schema.py` | 输入长度校验、输出白名单；非法输入 422 |
| 6.2 代码 6-2-3～6-2-8 | crud、service、controller 的新增/详情/删除 | `crud.py`、`service.py`、`controller.py` | 新增 201、重复 400、详情 200/404、删除 204/404 |
| 6.2 测试清单 | 九条接口检查 | `项目/tests/test_api.py`、`验证记录.md` | 九条全部有实测证据 |
| 6.3 代码 6-3-1 | 查询参数模型 | `项目/app/modules/department/param.py` | `page≥1`、`page_size` 1–100；非法值 422 |
| 6.3 代码 6-3-2、6-3-4、6-3-5 | offset/limit 与列表组装 | `crud.py` 的 `list_page`、`service.py` 的 `list_departments`、`controller.py` 的列表接口 | 分页切片正确、`total` 为全量条数、固定排序 |
| 6.3 代码 6-3-3 | 响应 `{items, total}` | 列表响应 | 只返回 items 或漏 total 均不合格 |
| 6.4 | 错误分层 | `分步实现指南.md` 阶段 4；`验证记录.md` 第三节 | 422 / 400 / 404 / 500 各归其位 |
| 实训 6-1 步骤 1 | 建库与建表 | `分步实现指南.md` 阶段 1–2 | `/health` 200，表已建立，seed 后 `count()=2` |
| 实训 6-1 步骤 2 | department 读写全流程 | 指南阶段 3 | 六文件齐备，分页与四类错误可复现 |
| 实训 6-1 步骤 3 | 验证与提交 | 指南阶段 4–5；`验证记录.md` | 九条通过、重启后数据仍在、工作区干净 |

简化说明：课堂固定单位示例；`users`、认证、权限、测试框架都不提前出现。教材 6-3-4 把 `offset` 计算写在 service 的调用处，本参考按 `duty-simplified` 的写法把 `offset` 计算放在 service、`crud.list_page` 只接收 `offset` 与 `limit`，语义与代码 6-3-2 一致。`tests/` 只作教师验证，不要求学生编写。

## 三、边界

- 不建 `users` 表，不引入 `app/core/security.py`、认证、令牌、权限；这些属于第 8、9 章。
- 不加 `/api/v1` 前缀；模块 router 为 `/departments`，根装配 `prefix=""`。
- 数据库为 SQLite，文件名 `duty.db`；`app/core/database.py` 只提供 `engine`、`SessionLocal`、`Base`、`get_db`。
- department 字段只有 `dept_code`（主键）、`full_name`、`address`；不得增加字段。
- 分页只接收 `page`（默认 1）与 `page_size`（默认 10，上限 100）；排序由后端固定为 `dept_code` 升序，前端不传 `sort_by`。
- 状态码契约不变：列表 200、详情 200、新增 201、修改 200、删除 204 无正文、重复编码 400、不存在 404、模型校验 422。
- `main.py` 只增加建表三行与幂等 seed（D001 一中队 / D002 二中队），不写业务规则。
- 不建 `tests/` 之外的新结构；本实训的 `tests/` 仅供教师验证，学生不必完成。
- `venv/`、`*.db`、`.env`、`__pycache__/` 不进入仓库；验证环境与运行数据库放在系统临时目录。

## 四、准备

1. Python 3.10 及以上、Git 可用；执行 `python --version`、`git --version` 检查。
2. 已完成实训 5-1，能说明六文件职责与五个单位接口；本参考直接提供其完成态作为 `starter/`。
3. 阅读教材 6.1–6.4，重点看代码 6-1-1、6-1-2、6-2-1～6-2-8、6-3-1～6-3-5。
4. 学生把 `starter/` 复制到可写工作目录，不直接修改教师 `项目/`。
5. 教师课前按 `验证记录.md` 复跑；课堂文档端口统一为 8000，本参考实测使用 8013 以避免冲突。
6. 保留 5-1 的接口验证记录，本实训结束时要补充持久化与分页证据。

## 五、时间

180 分钟覆盖教材三步，并把 44 分钟排错显式排入（约 24%）。标「选做」的内容不占必做时间。

| 阶段 | 内容 | 分钟 | 其中排错 | 必做/选做 |
| --- | --- | ---: | ---: | --- |
| 准备 | 环境检查、复制 starter、复核 5-1 产物 | 10 | 0 | 必做 |
| 阶段 1 | 新建 `app/core/database.py` 与包文件 | 20 | 5 | 必做 |
| 阶段 2 | 改 `model.py`，对齐 `schema.py`，`main.py` 建表与 seed | 25 | 6 | 必做 |
| 阶段 3 | 读写接线：`crud.py`、`service.py`、`param.py`、`controller.py` | 60 | 14 | 必做 |
| 阶段 4 | 走九条测试清单，核对 422/400/404 | 25 | 6 | 必做 |
| 阶段 5 | 重启持久化验证、更新 README 与记录 | 20 | 5 | 必做 |
| 阶段 6 | seed/init 拆分、分页边界、personnel 预告 | 课后 | — | 选做 |
| 验收 | 文件、接口、数据库、仓库卫生 | 10 | 0 | 必做 |
| 机动 | 集中排错与进度缓冲 | 10 | 8 | — |
|  | **合计** | **180** | **44** |  |

选做（课后或学有余力）：把 seed 与建表拆成独立初始化脚本；补充分页边界（越界页、`page_size` 上限调整、`total` 与过滤次序）；按第 7 章预告为 personnel 模块复用查询。

若进度落后，不删「重启持久化」和「九条清单」，可把 seed 拆分、分页边界与 personnel 全部移到课后。

## 六、步骤

| 教材步骤 | 操作 | 产物 | 详细指导 |
| --- | --- | --- | --- |
| 1 | 新建 `app/core/` 与 `database.py`；把 `model.py` 改为 ORM，`main.py` 加建表三行与幂等 seed | 可连接的 SQLite 与 `departments` 表 | `分步实现指南.md` 阶段 1–2 |
| 2 | 改 `crud.py`、`service.py`、`param.py`、`controller.py`，接通 Session 与分页 | 五个接口可调用 | 阶段 3 |
| 3 | 走九条测试清单，验证 422/400/404/204 | 状态码证据 | 阶段 4 |
| 4 | 重启服务验证数据仍在，更新 README 与验证记录 | 持久化证据与文档 | 阶段 5 |
| 5 | 提交代码、依赖、忽略规则与记录 | 干净工作区 | `README.md` 第十一节 |
| 6 | seed/init 拆分、分页边界、personnel 预告 | 选做扩展 | 阶段 6（课后） |

每个阶段在指南中都有完整代码、验证命令与常见错误。代表完成态文件的代码块与 `项目/` 对应文件逐字一致。

## 七、文件

```text
实训6-1/
├── README.md
├── 分步实现指南.md
├── 验证记录.md
├── 难度评分.md
├── 接缝表.md
├── 学员版差异说明.md
├── 项目/                        # 完成态，17 个文件
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   ├── README.md
│   ├── app/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── database.py
│   │   └── modules/
│   │       ├── __init__.py
│   │       └── department/      # 六文件 + 空 __init__.py
│   └── tests/
│       └── test_api.py          # 教师验证用，学生不必编写
└── starter/                     # 5-1 完成态（内存版），15 个文件
    ├── 起点说明.md
    ├── main.py
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── README.md
    └── app/                     # 与实训 5-1 完成态逐字一致
```

完成态项目不含 `venv/`、`.env`、`duty.db`、`__pycache__/`、`.git/`，也不含 `users` 模块或 `security.py`。

## 八、快速开始

在 `项目/` 目录执行：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

打开 <http://127.0.0.1:8000/docs>，另开终端请求：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/departments
```

教师验证需在临时虚拟环境另装 `pytest`、`httpx`，然后在实训根目录执行：

```powershell
python -m pytest 项目\tests -q
```

测试会把 `DATABASE_URL` 指向系统临时目录，不会在仓库生成 `duty.db`。停止 uvicorn 按 `Ctrl+C`。若 PowerShell 激活脚本受限，直接使用 `venv\Scripts\python.exe` 调用 `pip` 与 `uvicorn`，不要关闭系统安全策略。

## 九、验收

必做项：

- [ ] `app/core/__init__.py` 与 `app/core/database.py` 存在，`engine`、`SessionLocal`、`Base`、`get_db` 可用。
- [ ] `model.py` 为 SQLAlchemy 模型，表名 `departments`，三个字段与约束正确；不再有 `TABLE`。
- [ ] `main.py` 导入模型并执行 `create_all`；seed 幂等，重复启动不重复写入 D001、D002。
- [ ] 没有 `users` 表、`security.py`、认证、令牌或权限代码。
- [ ] 列表返回 `{items, total}`，按 `dept_code` 升序；`page=1&page_size=2` 的切片与总数正确。
- [ ] `page=0`、`page_size=0`、`page_size=101` 返回 422。
- [ ] 详情 200/404；新增 201、重复编码 400；修改 200；删除 204 且无正文，再次删除 404。
- [ ] 新增记录后重启服务，记录仍在；删除 `duty.db` 才是重置。
- [ ] `requirements.txt` 含 `sqlalchemy`；`.gitignore` 排除 `*.db` 与 `*.db-journal`。
- [ ] 接口路径无 `/api/v1`；`/docs` 200。
- [ ] 教师运行 `pytest 项目\tests -q` 全绿（学生不必提交测试）。

选做项：

- [ ] seed 与建表拆成独立脚本，应用启动只负责建表。
- [ ] 补充分页边界用例并说明 `total` 与过滤条件的次序。
- [ ] 为 personnel 模块写出复用计划（不要求在本实训完成）。

教师实测证据见 `验证记录.md`，不能用预期值代替学生自己的实际结果。

## 十、排错

| 现象 | 先查什么 | 处理 |
| --- | --- | --- |
| `no such table: departments` | 模型是否导入、`create_all` 是否执行 | 在 `main.py` 建表前导入模型；确认 `create_all` 在导入之后 |
| 重启后单位记录消失 | 是否仍用内存版 `model.py`；数据库文件位置 | 确认 `crud` 已改用 `Session`；确认 `DATABASE_URL` 指向同一文件 |
| 每次启动多出重复单位 | seed 是否先查存在性 | 逐条 `filter(...).first()`，已存在则跳过 |
| 列表只有 `items` 没有 `total` | service 是否组装总数 | `crud.list_page` 同时返回 `items` 与 `total` |
| 翻页出现重复或顺序不稳定 | 本章的 `list_page` 还没带 `order_by` | 第 7 章 7.4 会补固定排序键；本章先记录现象 |
| 新增重复编码返回 500 | 是否先查重 | service 先 `get_by_code`，重复抛 400；数据库约束作最后防线 |
| 详情/删除不存在返回 500 | 是否直接访问空对象 | service 查不到抛 404 |
| `ModuleNotFoundError: app.core` | 是否缺 `app/core/__init__.py`，或不在项目根执行 | 补包文件；在含 `main.py` 的目录启动 |
| `sqlite3.OperationalError: database is locked` | 会话是否未关闭、写入是否未提交 | 确认 `get_db` 在 `finally` 关闭；crud 写入后 `commit` |
| 测试后仓库出现 `duty.db` | `DATABASE_URL` 是否在导入 `main` 后才设置 | 在导入应用前设置环境变量，或改用 `tmp_path` |
| `duty.db` 被 Git 跟踪 | 忽略规则是否在首次提交前生效 | `git rm --cached duty.db`，确认 `.gitignore` 含 `*.db` |
| 422 与 400 混淆 | 错误产生位置 | 输入模型校验是 422；业务规则（重复编码）是 400 |

## 十一、提交

学生提交四项：

1. 代码：`app/core/database.py`、`app/core/__init__.py`、改写后的 `model.py`、`crud.py`、`service.py`、`controller.py`、`schema.py`、`param.py`、`main.py`。
2. 根目录配置：`requirements.txt`（含 `sqlalchemy`）、`.gitignore`（含 `*.db`、`*.db-journal`）、更新后的 `README.md`。
3. 九条接口验证记录：新增 201、重复 400、缺字段 422、列表 200 且分页正确、详情 200、不存在 404、修改 200 且不存在 404、删除 204 无正文、重复删除 404；另附重启前后同一条记录仍在的证据。
4. 仓库卫生检查：`git status` 干净，`git ls-files` 不含 `venv/`、`.env`、`*.db`、`__pycache__/`。

提交前用 `git ls-files` 复核。教师完成态、`tests/`、难度评分与实测记录用于备课与验收，不代替学生操作。

## 十二、扩展

以下均为课后扩展，不占 180 分钟必做时间：

1. **seed 与 init 拆分（选做）**：把 `create_all` 与 seed 移到独立脚本，应用启动只负责建表，比较两种做法在部署时的差异。
2. **分页边界（选做）**：验证 `page` 超过总页数返回空 `items` 与正确 `total`；讨论 `page_size` 上限为什么设 100。
3. **导出与备份**：用 SQLite 文件复制或 `.dump` 备份 `duty.db`，说明为什么不能只备份内存列表。
4. **索引依据**：`dept_code` 已由主键建立索引；为将来 personnel 的 `dept_code` 过滤设计索引并说明依据。
5. **人员模块预告**：按教材「课后拓展」把六文件复制为 personnel，新增时先校验 `dept_code` 是否存在，不存在返回 400；完整过滤与排序在第 7 章完成。
6. **复习**：回看第 4 章 4.2（表、主键、外键）与第 3 章 3.5（Pydantic 校验），说明同一类错误在表结构、输入模型与 service 三层分别由谁拦住。
