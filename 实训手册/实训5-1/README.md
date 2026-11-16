# 实训 5-1 实训手册：项目初始化与版本控制

> **对应教材**：第 5 章《项目初始化与版本控制》◆ 实训 5-1  
> **课次**：课次 6（4 学时 · 实践）｜前置：第 4 章实训 4-1 的产物；第 3 章 3.4（`APIRouter`）  
> **交付**：项目仓库、更新后的设计文档、验收记录

## 一、实训概览

| 项目 | 内容 |
| --- | --- |
| 实训编号 | 实训 5-1 |
| 实训名称 | 项目初始化与版本控制 |
| 对应教材 | 第 5 章 5.1–5.6 |
| 课次与学时 | 课次 6 · 4 学时 · 实践（180 分钟） |
| 组织形式 | 独立完成；分支与合并按个人仓库操作 |
| 场地与工具 | 可运行 Python 的计算机；已安装 Git；终端；浏览器 |
| 配套文件 | [分步实现指南.md](分步实现指南.md)、[项目/](项目/)、[验收记录.md](验收记录.md) |

本次实训以 4-1 的产物为起点，补全为可启动、可回溯、可在另一台机器上运行的仓库。工程只建**当前用到的文件**：入口、一个模块的接口与模型、四份配置。第 4 章 4.5 的六文件模板仍然有效，但另外四个文件要到第 8 章第一次读写数据时才加入。

## 二、学习目标与验收标志

### 2.1 本课结束后应能做到

| 编号 | 学习目标（能做什么） | 对应第 5 章目标 | 达标要点 |
| --- | --- | --- | --- |
| L1 | 说明最小工程里每个文件的职责，并解释 `main.py` 如何把模块装配为应用 | 2 | 能从一个 URL 说出经过的文件；能说明为什么暂不建其余文件 |
| L2 | 建立虚拟环境、编写依赖清单，并用 `.env.example` 与 `.env` 分离配置 | 3 | 能说明“装到哪个环境”“换机怎么复现”“哪些值不进仓库” |
| L3 | 完成 Git 初始化、暂存、提交，写出可读的提交信息，并用 `.gitignore` 排除环境与密钥 | 4、5 | 每次提交只含一项改动；`git status` 中不出现 `venv/`、`.env`、`*.db` |
| L4 | 建立分支、完成一次合并，并正确处理冲突 | 4 | 三组冲突标记已删除；历史中能看到分支与合并 |
| L5 | 以 4-1 产物为起点，把两个文件迁入最小工程并验证可启动 | 6 | `/health` 200、`/docs` 200、模块接口可调用 |

第 5 章目标 1（版本控制解决覆盖、丢失、无法回退三类问题）在课前阅读中完成；出口检查第 1 题会核对该理解。

### 2.2 验收标志

| 目标 | 验收标志 |
| --- | --- |
| 项目能启动 | `uvicorn main:app` 后可访问 `/health` 与 `/docs` |
| 目录与 5.1 一致 | `main.py`、`app/modules/<模块>/{controller,schema}`、四份根目录配置齐备 |
| 文件职责说明 | 能说明每个已建文件的职责，以及未建文件为何暂不建、何时加入 |
| 依赖可复现 | `pip install -r requirements.txt` 能装齐；`.env.example` 列出所需变量 |
| Git 历史可读 | 至少 3 次提交，信息说明做了什么 |
| 分支合并完成 | 有一次分支开发与合并记录 |

验收标志衡量交付物，学习目标衡量能力；两者冲突时以学习目标为准。例如仓库能启动、提交有三条，但说不清 `venv/` 为什么不能提交，L3 记为未达成。

### 2.3 本课知识点与教材位置

| 知识点 | 掌握程度 | 教材位置 |
| --- | --- | --- |
| 最小工程与文件职责 | 能说出 `main.py`、模块两文件、配置各管什么 | 5.1 |
| 一条请求的调用路径 | 能说出从 URL 到响应的经过 | 5.1；图 5-1 |
| 版本控制的三类问题 | 能说明覆盖、丢失、无法回退 | 5.2 |
| 工作区、暂存区、本地仓库 | 能说明 `add` 与 `commit` 各做什么，提交粒度如何选择 | 5.3 |
| 分支与冲突 | 能建分支、合并、处理三组冲突标记 | 5.4 |
| 虚拟环境与依赖清单 | 能建环境、激活、安装、说明复现方式 | 5.5 |
| 配置外置 | 能区分 `.env.example` 与 `.env`，说明哪个进仓库 | 5.6 |

## 三、本次实训的边界

**本实训不做的**（留给后续章）：

| 不做的事 | 留给哪一章 |
| --- | --- |
| 数据库与会话（`app/core/database.py`、`get_db`） | 第 6 章 |
| 认证（`app/core/security.py`） | 第 6 章 |
| 模块的 `model.py`、`crud.py`、`service.py`、`param.py` | 第 8 章 |
| pytest 与 `tests/` | 第 12 章 |
| 远程仓库、多人协作、代码评审 | 由课程另行安排 |

判断标准不是“文件越多越完整”，而是“每个已建文件都有当下用途”。空文件只占位置，不承担职责。

## 四、课前准备

### 4.1 知识准备

- [ ] 读过 5.1–5.6，能说出工作区、暂存区、本地仓库三者的关系
- [ ] 能复述 4-1 的产物：设计文档、`main.py`、`schemas.py`、接口验证记录
- [ ] 能说出模块两文件（controller、schema）各管什么

### 4.2 环境准备

| 项 | 要求 | 检查方法 |
| --- | --- | --- |
| Python | 3.10 及以上 | `python --version` |
| Git | 已安装 | `git --version` |
| Git 身份 | 已配置用户名与邮箱 | `git config --global user.name` |
| 4-1 产物 | 设计文档、`main.py`、`schemas.py`、接口验证记录 | 文件可打开 |

首次使用 Git 时先配置身份，否则提交会失败：

```bash
git config --global user.name "你的姓名"
git config --global user.email "你的邮箱"
```

### 4.3 材料准备

1. 在 4-1 的项目目录上继续，或新建 `duty/` 后按步骤 1 建目录。[项目/](项目/) 是完成后的完整工程，用于对照与自查，不直接复制。
2. 打开 4-1 的设计文档，确认“模块目录”一节可作为迁移清单。
3. 准备 [验收记录.md](验收记录.md) 的电子副本，按本人学号命名。

## 五、时间安排

| 步骤 | 内容 | 分钟 |
| --- | --- | ---: |
| — | 课前环境检查与启动练习 | 10 |
| 1 | 迁移 4-1 产物 | 15 |
| 2 | 补全配置并装配 `main.py` | 25 |
| 3 | 虚拟环境与依赖清单 | 20 |
| 4 | Git 初始化与首次提交 | 30 |
| 5 | 分支开发与合并 | 35 |
| 6 | 启动验证与提交 | 20 |
| — | 验收记录与出口检查 | 10 |
| — | 机动（排错、补漏） | 15 |
| — | 合计 | 180 |

时间不足时，优先保住步骤 4、5：Git 的历史与分支是本课不可替代的部分。

## 六、操作步骤

每一步给出四项内容：做什么、预期输出、做错会看到什么、本步检查点。检查点未通过时不进入下一步。

### 步骤 1：迁移 4-1 产物（15 分钟）

**做什么**

1. 新建 `app/modules/workstation/`，每个包目录放一个空的 `__init__.py`。
2. 把 4-1 的 `schemas.py` 内容移入 `schema.py`，内容不变。
3. 把 4-1 `main.py` 中的三个接口移入 `controller.py`；模块 `router` 的前缀写 `"/workstations"`，`/api/v1` 由根目录 `main.py` 提供。
4. 删除 `controller.py` 中的 `app = FastAPI()`；应用留给根目录 `main.py`。
5. 把设计文档“模块目录”一节改为实际目录。

**关键点**：4-1 的 `main.py` 同时含应用与接口。迁移后，应用归入口，接口归模块；两段前缀分别写在两处。

**预期输出**：

```bash
python -c "from app.modules.workstation import controller; print(controller.router.prefix)"
```

输出 `/workstations`。

**做错会看到什么**

- 文件仍在根目录、模块目录为空：后续路径都不匹配，应先迁移。
- `AttributeError: ... has no attribute 'router'`：`controller.py` 仍是 4-1 的写法，或删掉了 `router = APIRouter(...)`。
- `ModuleNotFoundError: No module named 'schemas'`：导入未改为 `app.modules.workstation.schema`。

**检查点**

- [ ] `controller.py` 只有 `router` 与接口函数，没有 `app = FastAPI()`
- [ ] `schema.py` 只有模型
- [ ] `router.prefix` 为 `/workstations`

### 步骤 2：补全配置并装配 `main.py`（25 分钟）

**做什么**：写 `requirements.txt`、`.env.example`、`.gitignore`、`README.md`；写根目录 `main.py`。

**requirements.txt**

```text
fastapi
uvicorn[standard]
pydantic
```

**.gitignore**

```gitignore
venv/
__pycache__/
*.pyc
.env
*.db
logs/
.pytest_cache/
```

**.env.example**

```env
SECRET_KEY="change-me-in-env"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
```

`.env.example` 进仓库，`.env` 不进；本章只建文件，读取从第 6 章起（`os.getenv`）。

**main.py**

```python
"""Duty API 入口：只负责创建应用与挂载路由。

对应教材第 5 章 5.1：入口不写业务代码。
第 6 章会在这里补建表三行：导入 Base 与 engine、导入模型、调用 create_all。
"""

from fastapi import FastAPI

from app.modules.workstation import controller as workstation_controller

# 应用对象：所有路由最终都挂在它上面，/docs 页面也由它生成。
app = FastAPI(title="Duty API", version="0.1.0")


# 健康检查：不查数据库、不做业务，只回答“服务是否在运行”。部署后也是第一项可用性证据。
@app.get("/health")
def health():
    return {"status": "healthy"}


# 把模块路由挂到应用。模块 router 的前缀是 "/workstations"，这里再加 "/api/v1"，
# 两段相加才是完整路径 /api/v1/workstations/；缺一段就会出现 404。
app.include_router(workstation_controller.router, prefix="/api/v1")
```

本章不建数据库，因此不写 `create_all`；第 6 章建立用户表时再补三行导入与建表。

**预期输出**：`/health` 200、`/docs` 200、模块接口路径为 `/api/v1/workstations/`。

**做错会看到什么**

- `/docs` 404：启动的不是根目录 `main.py`，或 `include_router` 漏写 `prefix`。
- 接口全 404、`/health` 正常：两段前缀只写了一段。
- `ModuleNotFoundError: app.core.database`：照抄了后续章节的代码；本章还没有该文件，删除导入。

**检查点**

- [ ] `python -c "import app"` 在项目根不报错
- [ ] `/health` 与 `/docs` 均 200
- [ ] `main.py` 只做创建应用与挂路由两件事

### 步骤 3：虚拟环境与依赖清单（20 分钟）

**做什么**

```bash
python -m venv venv
```

Windows 激活：

```bash
venv\Scripts\activate
```

Linux 或 macOS 激活：

```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

**预期输出**：提示符前出现 `(venv)`；`pip list` 可见 fastapi、uvicorn、pydantic。

**做错会看到什么**

- 提示符前没有 `(venv)`：激活失败或换了终端，依赖会装进系统 Python。
- PowerShell 提示“禁止运行脚本”：改用 `cmd`，或按提示调整执行策略。
- 换机后版本不同：教学环境先不锁版本；正式项目应写 `fastapi==x.y.z`。

**检查点**

- [ ] `python -c "import sys; print(sys.prefix)"` 指向项目内 `venv`
- [ ] `pip list` 能看到三项依赖
- [ ] `venv/` 未出现在 `git status` 中（步骤 4 验证）

### 步骤 4：Git 初始化与首次提交（30 分钟）

**做什么**

```bash
git init -b main
git add .gitignore
git commit -m "chore: add gitignore"
git status
git add .
git commit -m "chore: init fastapi project"
```

先单独提交 `.gitignore`，再执行 `git add .`，排除规则才生效。

**预期输出**：`git log --oneline` 显示两条提交；`git status` 显示 `nothing to commit, working tree clean`；`venv/`、`.env`、`*.db`、`logs/` 均未被跟踪。

**做错会看到什么**

- `git status` 出现 `venv/`：`.gitignore` 未生效或路径写错；已被跟踪时 `git rm -r --cached venv` 后提交移除。
- `.env` 已被提交：`git rm --cached .env`；密钥泄露须更换。
- 提交为空：文件被忽略规则误伤，先看 `git status`。
- 提示 `Please tell me who you are`：先配置 `user.name` 与 `user.email`。

**检查点**

- [ ] 至少 2 条提交，信息能说明做了什么
- [ ] `git ls-files` 中无 `venv/`、`.env`、`*.db`、`logs/`
- [ ] 工作区干净

### 步骤 5：分支开发与合并（35 分钟）

**做什么**：在分支上修改 `/health`，再合并回 `main`；按下列顺序可稳定复现一次冲突。

```bash
git switch -c feature/health-version
```

在分支上把 `/health` 改为：

```python
return {"status": "healthy", "version": "0.1.0"}
```

```bash
git add main.py
git commit -m "feat: add version to health check"
git switch main
```

在 `main` 上把同一行改为：

```python
return {"status": "ok"}
```

```bash
git add main.py
git commit -m "feat: simplify health status"
git merge feature/health-version
```

冲突文件出现三组标记：

```text
<<<<<<< HEAD
当前分支的内容
=======
要合并进来的内容
>>>>>>> feature/health-version
```

保留 `return {"status": "healthy", "version": "0.1.0"}`，删除三组标记，然后：

```bash
git add main.py
git commit -m "merge: combine health status and version"
```

**预期输出**：`git log --oneline --graph` 能看到分支与合并；`main.py` 中无冲突标记；重启后 `/health` 返回合并结果。

**做错会看到什么**

- 提交提示 “You have not concluded your merge”：标记未删净或未 `git add`。
- 历史是一条直线：分支上没提交，合并成了空操作。
- `/health` 仍是旧值：改完未重启，或改在错误分支。

**检查点**

- [ ] 三组标记全部删除
- [ ] 历史含分支与合并
- [ ] `/health` 为合并后的结果

### 步骤 6：启动验证与提交（20 分钟）

**做什么**

1. 重新启动服务，验证 `/health`、`/docs` 与三个接口。
2. 填写 [验收记录.md](验收记录.md)。
3. 设计文档“模块目录”一节更新为实际目录；不一致处记录判定。
4. 提交文档：

```bash
git add -A
git status
git commit -m "docs: update project structure"
```

**预期输出**：`/health` 200、`/docs` 200、接口可调用；`git log` 至少 3 条；工作区干净；文档与磁盘一致。

**做错会看到什么**

- 文档路径与磁盘不一致：以实际目录改文档，并记录差异。
- `git add -A` 带入不应提交的文件：先看 `git status` 再提交。
- 提交信息写“update”：后续无法判断改动，重写为说明做了什么。

**检查点**

- [ ] 三条验收证据齐全：`/health`、`/docs`、接口
- [ ] 设计文档目录与实际一致
- [ ] 工作区干净，提交信息可读

## 七、配套项目文件

```text
实训5-1/
├── README.md          本手册
├── 分步实现指南.md     六个阶段的代码、命令与验证（教师演示／自查）
├── 验收记录.md        启动、目录、Git 历史与排除项记录（学生填写）
└── 项目/              完成后的最小工程，可直接启动
    ├── main.py
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── README.md
    └── app/
        ├── __init__.py
        └── modules/
            ├── __init__.py
            └── workstation/
                ├── __init__.py
                ├── controller.py
                └── schema.py
```

使用方式：从 4-1 的产物开始，按 [分步实现指南.md](分步实现指南.md) 逐阶段推进；[项目/](项目/) 是全部阶段完成后的状态，可直接启动，也可与自己的实现逐文件比对。提交时不得把 `项目/` 原样提交，须替换为自己的业务对象与模块名。

## 八、验收标准

按四项判定，建议权重如下：

| 验收项 | 判定内容 | 权重 |
| --- | --- | ---: |
| 项目能启动 | `/health` 200、`/docs` 200，模块接口可调用 | 25 |
| 目录与配置一致 | 与 5.1 一致；依赖清单与 `.env.example` 完整 | 25 |
| Git 历史可读 | 至少 3 次提交，信息说明做了什么；无 `venv/`、`.env`、`*.db` | 25 |
| 分支合并完成 | 一次分支开发与合并，冲突已正确处理 | 25 |

判定尺度：

- **通过**：四项均达到判定内容，出口检查五题中至少四题答出。
- **部分通过**：某项缺一到两条，例如提交信息不可读、配置缺项；或出口检查三题及以上答不出。限期补齐。
- **不通过**：服务无法启动、仓库含 `venv/` 或 `.env`、无分支记录。

提交前自检：

- [ ] `/health` 与 `/docs` 均有实际结果记录
- [ ] `python -c "import app"` 在项目根不报错
- [ ] `git ls-files` 中无 `venv/`、`.env`、`*.db`、`logs/`
- [ ] 提交信息至少三条，且能读出做了什么
- [ ] 冲突文件无三组标记
- [ ] 设计文档目录与实际一致

## 九、排错清单

| 现象 | 先查什么 |
| --- | --- |
| 服务起不来 | 端口占用、依赖缺失、语法错误 |
| `/docs` 打不开 | 启动文件是否为根目录 `main.py`、`include_router` 前缀是否写全 |
| 接口全 404 | 两段前缀是否都写、单复数是否一致 |
| `ModuleNotFoundError: app` | 包目录是否缺 `__init__.py`、是否在项目根目录执行 |
| `ModuleNotFoundError: app.core.database` | 本章还没有该文件；删除导入，第 6 章再加入 |
| 依赖装到系统环境 | 虚拟环境是否激活：`python -c "import sys; print(sys.prefix)"` |
| 提交为空 | `git status`、`.gitignore` 是否误伤所需文件 |
| `venv/` 已被跟踪 | `git rm -r --cached venv` 后提交移除 |
| `.env` 已被跟踪 | `git rm --cached .env`；泄露的密钥应更换 |
| 合并冲突 | 保留目标内容，删除三组标记后再 `git add` |
| 换台机器无法运行 | 依赖是否锁定、`.env.example` 是否列全 |
| 提交提示未配置身份 | `git config --global user.name` 与 `user.email` |

## 十、提交要求

提交三项：**项目仓库**、**更新后的设计文档**、**验收记录**。

```text
学号-姓名-实训5-1/
├── duty/             项目仓库，含 .git 目录
├── 设计文档.md        更新目录一节后的版本
└── 验收记录.md
```

要求：

1. 仓库须包含 `.git`，教师据此核对提交历史、分支与合并记录。
2. 不要打包 `venv/`、`.env`、`*.db`、`logs/`。
3. 设计文档与实际目录不一致处，须在验收记录中写明判定。
4. 验收记录须填实际命令输出，不接受只写“成功”。

## 十一、课后扩展

- 为项目补充 `README.md`，写明启动命令与目录说明。
- 将配置项补入 `.env.example`，并验证另一台机器可依据文档完成安装。
- 练习一次 `git revert` 或 `git reset` 的安全回退，记录回退前后 `git log` 的变化。
- **复习任务**：回看 3.4（`APIRouter`）、4.5（六类职责）与 5.1（工程目录），说明当前工程复用了前两章的哪些机制，并指出哪些文件要到第 6、8 章才加入。

## 十二、下课前的出口检查（10 分钟）

交付物衡量“做完了没有”，出口检查衡量“学会了没有”。答不出的题，回到对应步骤与教材节号补齐；五题中三题及以上答不出，本次实训记为部分通过。

| 题号 | 问题 | 达标要点 | 目标 | 自评 |
| ---: | --- | --- | --- | --- |
| 1 | 版本控制解决哪三类问题？为什么“复制备份文件”不算版本控制？ | 覆盖、丢失、无法回退；备份不记录修改内容与差异 | L3 前置 | □ 能 □ 需查 □ 不能 |
| 2 | 最小工程里每个文件负责什么？为什么这四个文件暂时不建？ | 入口装配、controller 接请求、schema 管进出；无职责的空文件只占位置 | L1 | □ 能 □ 需查 □ 不能 |
| 3 | `venv/`、`.env` 为什么都不能提交？各自理由是什么？ | 体积大且可复现；含密钥 | L2、L3 | □ 能 □ 需查 □ 不能 |
| 4 | 一次提交应包含多少改动？提交信息怎么写？冲突怎么处理？ | 一次一项改动；类型前缀说明做了什么；删三组标记后 `add` 再 `commit` | L3、L4 | □ 能 □ 需查 □ 不能 |
| 5 | 从 4-1 的两个文件到本实训的工程，多了哪些文件？各自解决什么问题？ | 入口、模块目录、依赖清单、配置、忽略规则、版本记录 | L5 | □ 能 □ 需查 □ 不能 |

自评说明：**能**＝不看教材可完整回答并举例；**需查**＝能说大意，细节需翻书；**不能**＝答不出。教师在步骤 6 后随机抽两题口头检查。

## 附录 A：常用 Git 命令

| 目的 | 命令 |
| --- | --- |
| 初始化仓库（主分支为 main） | `git init -b main` |
| 查看状态 | `git status` |
| 查看历史 | `git log --oneline --graph` |
| 暂存全部改动 | `git add .` |
| 暂存指定文件 | `git add main.py` |
| 提交 | `git commit -m "feat: add health endpoint"` |
| 创建并切换分支 | `git switch -c feature/health-version` |
| 切换分支 | `git switch main` |
| 合并分支 | `git merge feature/health-version` |
| 查看已跟踪文件 | `git ls-files` |
| 从索引移除已跟踪文件 | `git rm --cached .env` |

## 附录 B：预期输出对照

**工作区干净**

```text
On branch main
nothing to commit, working tree clean
```

**历史可读**

```text
*   e4f1a2b (HEAD -> main) merge: combine health status and version
|\
| * 9c2d7e1 (feature/health-version) feat: add version to health check
* | 3a8b5c0 feat: simplify health status
|/
* 7d1e4f9 chore: init fastapi project
* 2b6c8a3 chore: add gitignore
```

**排除项检查**

```bash
git ls-files | grep -E "venv/|\.env$|\.db$|logs/|__pycache__"
```

无输出即为正确；有输出说明对应文件已被跟踪，按排错清单移除。命令中的 `grep` 需在 Git Bash 中执行；Windows 命令提示符可改为逐项检查：

```bat
git ls-files | findstr venv
git ls-files | findstr .env
git ls-files | findstr .db
```
