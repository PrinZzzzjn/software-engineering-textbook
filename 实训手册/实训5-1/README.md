# 实训 5-1 实训手册：项目初始化与版本控制

> **对应教材**：第 5 章《项目初始化与版本控制》章末 ◆ 实训 5-1
> **课次**：课次 6（4 学时 · 实践，180 分钟）｜前置：第 4 章综合实训 4-1 的六文件实现；第 4 章 4.6
> **交付**：工程仓库、设计文档更新、`/health` 与 `/docs` 验证记录、Git 历史

## 一、实训概览

| 项目 | 内容 |
| --- | --- |
| 实训编号 | 实训 5-1 |
| 实训名称 | 项目初始化与版本控制 |
| 对应教材 | 第 5 章 5.1–5.6 |
| 课次与学时 | 课次 6 · 4 学时 · 实践（180 分钟） |
| 组织形式 | 独立完成 |
| 场地与工具 | 可运行 Python 的计算机；终端；已安装 Git；浏览器 |
| 配套文件 | [验收记录.md](验收记录.md)、[项目/](项目/) |

本实训以 4-1 的六文件产物为起点，把它迁入完整工程目录，再补上依赖清单、虚拟环境、配置、忽略规则与 Git 历史。**不新建模块文件**，也不改五个接口的行为。

## 二、学习目标与验收标志

| 编号 | 学习目标（能做什么） | 对应第 5 章目标 | 达标要点 |
| --- | --- | --- | --- |
| L1 | 说明工程目录中每个文件的职责，指出一条请求经过的文件 | 2 | 能沿 controller → service → crud → model 走通 |
| L2 | 创建虚拟环境、写依赖清单，并说明换机如何复现 | 3 | `pip install -r requirements.txt` 能装齐 |
| L3 | 完成 Git 初始化、提交、分支与合并，处理一次冲突 | 4 | 历史可读；分支与合并可见 |
| L4 | 写可读的提交信息，用 `.gitignore` 排除环境、数据库与密钥 | 5 | `git status` 干净；`venv/`、`.env`、`*.db` 未被跟踪 |
| L5 | 从 4-1 的六文件产物补全工程并验证服务可启动 | 6 | `/health` 200、`/docs` 200 |

### 验收标志

| 目标 | 验收标志 |
| --- | --- |
| 项目能启动 | `uvicorn main:app` 后可访问 `/health` 与 `/docs` |
| 工程目录与 5.1 一致 | 入口、`app/modules/<模块>/` 六文件与根目录配置齐备 |
| 文件职责说明 | 能说明六个文件各自的职责；`app/core/` 与 `tests/` 暂不建 |
| 依赖可复现 | `pip install -r requirements.txt` 能装齐；`.env.example` 列出所需变量 |
| Git 历史可读 | 至少 3 次提交，信息说明做了什么 |
| 分支合并完成 | 有一次分支开发与合并记录 |

## 三、本次实训的边界

| 不做的事 | 留给哪一章 |
| --- | --- |
| 数据库与建表 | 第 8 章 |
| 登录认证 | 第 6、7 章 |
| 自动化测试 | 第 12 章 |
| 修改五个接口的行为 | 本实训不改；只迁移与工程化 |

## 四、课前准备

- Python 3.10+ 与 Git 已安装。
- **4-1 的六文件产物**：`controller.py`、`service.py`、`crud.py`、`model.py`、`schema.py`、`param.py`。
- 一份从 5.1 抄录的工程目录清单。
- 打开 [验收记录.md](验收记录.md)。

## 五、时间安排

| 步骤 | 内容 | 分钟 |
| --- | --- | ---: |
| — | 课前环境检查与启动练习 | 10 |
| 1 | 迁移 4-1 六文件 | 15 |
| 2 | 补全配置并装配 `main.py` | 25 |
| 3 | 虚拟环境与依赖清单 | 20 |
| 4 | Git 初始化与首次提交 | 30 |
| 5 | 分支开发与合并 | 35 |
| 6 | 启动验证与提交 | 20 |
| — | 验收记录与出口检查 | 10 |
| — | 机动（排错、补漏） | 15 |
| — | **合计** | **180** |

时间不足时，优先保住步骤 4、5：Git 历史与分支是本课不可替代的部分。

## 六、操作步骤

### 步骤 1：迁移 4-1 六文件（15 分钟）

**做什么**

1. 新建 `app/`、`app/modules/`、`app/modules/<模块>/`，每个包目录放一个空的 `__init__.py`。
2. 把 4-1 的六个文件整体移入模块目录，文件名不变。
3. 删除 `controller.py` 中的 `app = FastAPI()`；应用留给根目录 `main.py`。
4. 模块 `router` 的前缀写资源名，例如 `"/departments"`；`/api/v1` 由根目录 `main.py` 提供。
5. 把设计文档“模块目录”一节改为实际目录。

**关键点**：4-1 的六文件已经职责分明，本步只改位置与装配，不改逻辑。

**预期输出**：

```bash
python -c "from app.modules.dept import controller; print(controller.router.prefix)"
```

输出 `/departments`。

**做错会看到什么**

- 文件仍在根目录、模块目录为空：后续路径都不匹配，应先迁移。
- `AttributeError: ... has no attribute 'router'`：`controller.py` 中删掉了 `router = APIRouter(...)`。
- `ModuleNotFoundError: No module named 'app.modules'`：包目录缺 `__init__.py`，或未在项目根目录执行。

**检查点**

- [ ] 模块目录下六个文件齐备
- [ ] `controller.py` 只有 `router` 与接口函数，没有 `app = FastAPI()`
- [ ] `router.prefix` 为自选资源名

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
from fastapi import FastAPI

from app.modules.dept import controller as dept_controller

app = FastAPI(title="Duty API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(dept_controller.router, prefix="/api/v1")
```

**预期输出**：`/health` 200、`/docs` 200、模块接口路径为 `/api/v1/departments/`。

**做错会看到什么**

- `/docs` 404：启动文件或前缀不对。
- 接口全 404：`include_router` 的两段前缀缺一。
- `ModuleNotFoundError: app.core.database`：本章还没建该文件，应删除导入。

### 步骤 3：虚拟环境与依赖清单（20 分钟）

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
pip install -r requirements.txt
```

**预期输出**：提示符前出现 `(venv)`；`pip list` 可见所列依赖。

**做错会看到什么**：依赖装入系统环境；换机后版本不一致。

### 步骤 4：Git 初始化与首次提交（30 分钟）

```bash
git init -b main
git add .gitignore
git commit -m "chore: add gitignore"
git add .
git commit -m "chore: init fastapi project"
```

**预期输出**：`git log` 有 2 条提交；`venv/`、`.env`、`*.db`、`logs/` 均未被跟踪。

**做错会看到什么**：`git status` 出现 `venv/`：`.gitignore` 未生效或路径写错；已跟踪时用 `git rm -r --cached venv`。

### 步骤 5：分支开发与合并（35 分钟）

```bash
git switch -c feature/health-version
# 修改 /health 的返回值
git add main.py
git commit -m "feat: add service version to health"
git switch main
git merge feature/health-version
```

按教师要求制造并解决一次冲突：保留所需内容，删除 `<<<<<<<` 三组标记，`git add` 后再 `git commit`。

**预期输出**：历史可读，分支与合并可见。

### 步骤 6：启动验证与提交（20 分钟）

- 重新启动服务，确认 `/health` 200、`/docs` 200、五个接口可调用。
- 把设计文档的目录一节更新为实际目录。
- 填写 [验收记录.md](验收记录.md)，完成出口检查。

## 七、配套项目文件

`项目/` 是完成后的完整工程，可作为对照：

```text
项目/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── app/
    └── modules/
        └── dept/
            ├── __init__.py
            ├── controller.py
            ├── service.py
            ├── crud.py
            ├── model.py
            ├── schema.py
            └── param.py
```

## 八、快速开始

```bash
cd 项目
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

打开 `http://127.0.0.1:8000/docs`，应看到“单位”分组与五个端点。

## 九、验收标准

| 项目 | 通过标准 |
| --- | --- |
| 启动 | `/health` 200、`/docs` 200 |
| 目录 | 六文件与四份根目录配置齐备 |
| 职责说明 | 能沿 controller → service → crud → model 走通一条请求 |
| 依赖 | 换目录执行 `pip install -r requirements.txt` 能装齐 |
| Git | 至少 3 次提交，信息可读；有一次分支合并 |
| 忽略规则 | `venv/`、`.env`、`*.db`、`logs/` 未被跟踪 |

## 十、排错清单

| 现象 | 先查什么 |
| --- | --- |
| 服务起不来 | 端口占用、依赖缺失、语法错误 |
| `/docs` 打不开 | 服务是否启动、启动文件是否为 `main:app` |
| 接口全 404 | `include_router` 的两段前缀是否都写 |
| `ModuleNotFoundError` | 包目录是否缺 `__init__.py`、是否在项目根目录执行 |
| 依赖装到系统环境 | 虚拟环境是否激活 |
| 提交为空 | `git status`、`.gitignore` 是否误伤 |
| 合并冲突 | 保留目标内容，删除三组标记后再 `git add` |
| 换台机器无法运行 | 依赖是否锁定、`.env.example` 是否列全 |

## 十一、提交要求

提交：更新后的设计文档、项目仓库、`git log`、`/health` 与 `/docs` 的验证记录。

## 十二、课后扩展

- 为项目补充 `README.md`，写明启动命令与目录说明。
- 把配置项补入 `.env.example`，验证另一台机器可依据文档完成安装。
- 练习一次 `git revert` 或 `git reset` 的安全回退。
- **复习任务**：回看第 3 章 3.3（`APIRouter`）、第 4 章 4.6（六文件与 `Depends`）与本章 5.1（工程目录），说明当前工程复用了前两章的哪些机制，并指出哪些文件要到第 6、12 章才加入。

## 十三、下课前的出口检查

- [ ] 六文件齐备，入口只做创建应用与挂路由。
- [ ] `/health` 200、`/docs` 200、五个接口可调用。
- [ ] 依赖清单、`.env.example`、`.gitignore`、`README.md` 齐备。
- [ ] `git log` 至少 3 条，信息可读。
- [ ] 有一次分支开发与合并记录。
- [ ] `venv/`、`.env`、`*.db`、`logs/` 未被跟踪。
