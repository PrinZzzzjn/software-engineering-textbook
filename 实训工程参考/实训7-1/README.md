# 实训 7-1：数据模块：查询复用（教师用工程参考）

> 对应教材：第 7 章 7.1–7.5 与章末「◆ 实训 7-1」  
> 学时：2 学时，共 90 分钟  
> 示例对象：单位（`department`）与人员（`personnel`）  
> 交付：两个模块的过滤分页接口、固定排序、改造前后回归记录

本目录是教师完整版，包含完成态、学员起点与真实实跑记录，不直接作为学生提交模板。学生从 `starter/`（6-1 完成态）出发，新增 personnel 模块，并把 department 已有的查询写法复用到第二个模块。

## 一、概览

| 项目 | 内容 |
| --- | --- |
| 主目标 | 把分页参数、过滤条件与固定排序收进「参数模型 + 模块内查询」这一套写法，并在两个模块中保持一致 |
| 复用演练 | personnel 模块六文件按 department 的同构写法落地，只改模型、过滤字段与排序键 |
| 综合验证 | department 过滤命中/未命中、personnel 分页与过滤、422 边界、改造前后 `items`/`total` 回归 |
| 数据方式 | SQLite 文件 `duty.db`；启动时建表并幂等 seed D001/D002 与 P001/P002 |
| 完成态入口 | `项目/main.py` |
| 学员起点 | `starter/起点说明.md` 与 6-1 完成态工程 |
| 教师验证 | 实训根目录执行 `pytest 项目\tests -q`，测试使用临时数据库 |
| 难度初评 | D3 / L4 / 偏紧（依据与取舍见 `难度评分.md`） |

本实训不新建业务表之外的认证结构，也不建 `users` 表。课堂增量是「查询写法复用 + 第二个模块」，不是重写一遍落库。认证与账号管理分别到第 8、9 章再加入。

## 二、目标

完成本实训后，学生应能：

1. 并排比较两个模块的 `list_page`，指出分页骨架相同，而模型、过滤字段与排序列属于各模块语义。
2. 把分页与过滤参数收进 `param.py`，用 `Field` 集中声明 `ge=1`、`le=100`，非法参数在进入函数前返回 422。
3. 在 `crud.py` 中先拼装 `filter`、再 `count()`，使 `total` 与 `items` 描述同一批过滤结果。
4. 为列表设置固定 `order_by`，不向前端暴露 `sort_by`，保证翻页稳定。
5. 把 department 的六文件写法复制到 personnel，只替换模型、过滤字段、排序键与业务校验。
6. 用同一组请求比对改造前后的 `items` 与 `total`，确认 6-1 的 department 行为没有回归。

### 教材映射表

| 教材位置 | 教材内容 | 工程参考落点 | 验收点 |
| --- | --- | --- | --- |
| 7.1 代码 7-1-1 | 两个模块 `list_page` 的共同骨架 | `department/crud.py` 与 `personnel/crud.py` 并排 | 能指出模型、过滤、排序三处差异 |
| 7.2 代码 7-2-1 | department 分页参数模型 | `项目/app/modules/department/param.py` | `page≥1`、`page_size` 1–100 |
| 7.2 代码 7-2-2 | personnel 带过滤参数模型 | `项目/app/modules/personnel/param.py` | `name`、`dept_code` 可选，空串不筛选 |
| 7.2 代码 7-2-3 | service 换算 `offset` 并组装 | 两个模块的 `service.py` | 只做换算与组装，不写边界判断 |
| 7.3 代码 7-3-1 | 过滤后计数 | `personnel/crud.py` 的 `list_page` | `filter` 在 `count()` 之前；过滤后 `total` 变化 |
| 7.4 代码 7-4-1 | 排序列白名单（讨论） | `分步实现指南.md` 阶段 4 | 说明本实训为何不暴露 `sort_by` |
| 7.4 代码 7-4-2 | 固定排序键 | 两个模块 `crud.py` 的 `order_by` | department 按 `dept_code`、personnel 按 `certificate_number` |
| 7.5 代码 7-5-1、7-5-2 | 公共 `paginate` 与复用边界 | 阶段 4 讨论；`README.md` 第十二节扩展 | 能判断哪些可收拢、哪些必须留在模块；公共件作为课后扩展 |
| 例 7-1 | 过滤后计数的分页查询 | `personnel/crud.py` | 带过滤时 `total` 与 `items` 同源 |
| 例 7-2 | 判断哪些代码可复用 | `分步实现指南.md` 阶段 1 | 主键查询/分页可收拢，业务校验留在模块 |
| 例 7-3 | 列表接口薄层透传 | 两个模块的 `service.py`、`controller.py` | service 组装二字段，controller 只声明契约 |
| 实训 7-1 步骤 1 | 找重复与差异 | 指南阶段 1 | 至少列出三处结构相同 |
| 实训 7-1 步骤 2 | 集中参数边界 | 指南阶段 2 | `page=0`、`page_size=0` 返回 422 |
| 实训 7-1 步骤 3 | 修正计数次序 | 指南阶段 3 | 过滤命中后 `total` 等于过滤结果总数 |
| 实训 7-1 步骤 4 | 固定排序并回归 | 指南阶段 4、6；`验证记录.md` | 翻页无重复；改造前后响应逐字段一致 |
| 实训 7-1 排错/提交 | 四项验收 | `README.md` 第十、十一节 | 四项均有实测证据 |

简化说明：教材 7.5 把「分页骨架」收拢到 `app/core/pagination.py`。本实训 90 分钟只保留「参数模型 + 过滤 + 固定排序」一个主目标，两个模块各自保留同构的 `list_page`，用代码并排与回归结果证明写法一致；公共 `paginate`、多字段组合过滤与分页边界列为课后扩展。`tests/` 只作教师验证，不要求学生编写。

## 三、边界

- 不建 `users` 表，不引入 `app/core/security.py`、认证、令牌、权限；这些属于第 8、9 章。
- 不加 `/api/v1` 前缀；模块 router 为 `/departments` 与 `/personnel`，根装配 `prefix=""`。
- department 字段仍只有 `dept_code`（主键）、`full_name`、`address`；不得增加字段。
- personnel 字段从 `duty-simplified` 取：`certificate_number`（主键）、`name`、`dept_code`、`rank`（可空）。
- 查询参数统一为 `page`、`page_size`；过滤字段使用各自表的列名：department 为 `full_name`，personnel 为 `name`、`dept_code`。
- 排序由后端固定：department 按 `dept_code` 升序，personnel 按 `certificate_number` 升序；不接受 `sort_by`。
- 状态码契约不变：列表 200、详情 200、新增 201、修改 200、删除 204 无正文、重复资源 400、不存在 404、模型校验 422。
- 过滤无命中返回 200 与 `{items: [], total: 0}`，不得返回 404。
- `main.py` 只增加 personnel 模型导入、路由挂载与 seed，不写业务规则。
- 本实训不新增 `app/core/pagination.py`；公共分页只在文档中讨论，作为课后扩展。
- `venv/`、`*.db`、`.env`、`__pycache__/` 不进入仓库；验证环境与运行数据库放在系统临时目录。

## 四、准备

1. Python 3.10 及以上；执行 `python --version` 检查。
2. 已完成实训 6-1，能说明 `engine`、`SessionLocal`、`Base`、`get_db` 与分页 `{items, total}`；本参考直接把 6-1 完成态作为 `starter/`。
3. 阅读教材 7.1–7.5，重点看代码 7-1-1、7-2-1～7-2-3、7-3-1、7-4-2、7-5-1～7-5-5。
4. 把 `starter/` 复制到可写工作目录，不直接修改教师 `项目/`。
5. 教师课前按 `验证记录.md` 复跑；课堂文档端口统一为 8000，本参考实测使用 8014。
6. 保留 6-1 的 department 验证记录，本实训结束时要补充过滤与回归证据。

## 五、时间

90 分钟只设一个主目标。personnel 是复用演练，多字段组合过滤与分页边界不占必做时间。

| 阶段 | 内容 | 分钟 | 其中排错 | 必做/选做 |
| --- | --- | ---: | ---: | --- |
| 准备 | 复制 starter、检查环境、确认 6-1 行为 | 5 | 0 | 必做 |
| 阶段 1 | 并排识别两个列表的重复与差异 | 10 | 2 | 必做 |
| 阶段 2 | 参数模型集中边界（department 加 `full_name`） | 10 | 2 | 必做 |
| 阶段 3 | 过滤条件拼装与计数次序 | 15 | 4 | 必做 |
| 阶段 4 | 固定排序与 department 四条检查 | 15 | 4 | 必做 |
| 阶段 5 | personnel 六文件复用演练 | 20 | 5 | 必做 |
| 阶段 6 | 回归 6-1 与提交 | 10 | 2 | 必做 |
| 验收 | 文件、接口、回归记录、仓库卫生 | 5 | 0 | 必做 |
|  | **合计** | **90** | **19** |  |

排错约占 21%。若进度落后，先保住 department 的过滤与固定排序、personnel 的列表分页；personnel 的完整增删改可留到课后补。多字段组合过滤、分页边界、`app/core/pagination.py` 均为课后扩展。

## 六、步骤

| 教材步骤 | 操作 | 产物 | 详细指导 |
| --- | --- | --- | --- |
| 1 | 并排两个 `list_page`，标出模型、过滤、排序三处差异 | 重复与差异清单 | `分步实现指南.md` 阶段 1 |
| 2 | 在 `department/param.py` 增加 `full_name`；personnel 参数模型沿用同一形状 | 参数模型与 422 边界 | 阶段 2 |
| 3 | 在 `crud.list_page` 中先 `filter` 后 `count`；service 透传过滤字段 | 过滤命中/未命中与正确 `total` | 阶段 3 |
| 4 | 两个模块固定 `order_by`，逐页比对无重复 | 稳定翻页与 department 检查 | 阶段 4 |
| 5 | 新建 personnel 六文件，按 department 同构改写；`main.py` 挂路由与 seed | personnel 五接口 | 阶段 5 |
| 6 | 用同一组请求回归 6-1 的 department 接口，更新 README 与记录 | 回归证据与干净工作区 | 阶段 6 |

每个阶段在指南中都有完整代码、验证命令与常见错误。代表完成态文件的代码块与 `项目/` 对应文件逐字一致。

## 七、文件

```text
实训7-1/
├── README.md
├── 分步实现指南.md
├── 验证记录.md
├── 难度评分.md
├── 接缝表.md
├── 学员版差异说明.md
├── 项目/                        # 完成态，24 个文件
│   ├── main.py                  # 两个 router + 两个模型导入 + 建表 + 两段 seed
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
│   │       ├── department/      # 六文件 + 空 __init__.py（param 增加过滤）
│   │       └── personnel/       # 六文件 + 空 __init__.py（数据库版）
│   └── tests/
│       └── test_api.py          # 23 项教师验证；学生不必编写
└── starter/                     # 6-1 完成态 + 起点说明，18 个文件
    ├── 起点说明.md
    ├── main.py
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── README.md
    ├── app/                     # 与实训 6-1 完成态逐字一致
    └── tests/test_api.py        # 6-1 教师测试，可用于回归
```

完成态项目不含 `venv/`、`.env`、`duty.db`、`__pycache__/`、`.git/`，也不含 `users` 模块、`security.py` 或 `app/core/pagination.py`。

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
Invoke-RestMethod "http://127.0.0.1:8000/departments?full_name=一"
Invoke-RestMethod "http://127.0.0.1:8000/personnel?page=1&page_size=1"
```

教师验证需在临时虚拟环境另装 `pytest`、`httpx`，然后在实训根目录执行：

```powershell
python -m pytest 项目\tests -q
```

测试会把 `DATABASE_URL` 指向系统临时目录，不会在仓库生成 `duty.db`。停止 uvicorn 按 `Ctrl+C`。若 PowerShell 激活脚本受限，直接使用 `venv\Scripts\python.exe` 调用 `pip` 与 `uvicorn`。

## 九、验收

必做项：

- [ ] department `param.py` 含 `page`、`page_size`、`full_name`；personnel `param.py` 含 `page`、`page_size`、`name`、`dept_code`。
- [ ] `page=0`、`page_size=0`、`page_size=101` 在两个列表都返回 422。
- [ ] department 按 `full_name` 模糊过滤，personnel 按 `name` 模糊、`dept_code` 精确过滤；空串视为不筛选。
- [ ] 过滤条件在 `count()` 之前；命中时 `total` 等于过滤结果总数，未命中返回 200 与 `{items: [], total: 0}`。
- [ ] 列表固定排序：department `dept_code` 升序，personnel `certificate_number` 升序；反复翻页无重复。
- [ ] personnel 六文件齐备，`main.py` 在 `create_all` 前导入两个模型，seed 含 D001/D002 与 P001/P002。
- [ ] 两个模块的详情 200/404、新增 201/400、修改 200、删除 204 且无正文、重复删除 404 均可用。
- [ ] department 的 6-1 行为未回归：路径、状态码、分页形状与固定排序不变。
- [ ] 没有 `users` 表、`security.py`、认证、令牌、权限代码，也没有 `/api/v1` 与 `sort_by`。
- [ ] 教师运行 `pytest 项目\tests -q` 全绿（学生不必提交测试）。

选做项：

- [ ] 验证 `name` 与 `dept_code` 同时传入的组合过滤。
- [ ] 验证越界页返回空 `items` 与正确 `total`，并讨论 `page_size` 上限为什么设 100。
- [ ] 按教材 7.5 抽出 `app/core/pagination.py`，比较「模块内同构写法」与「公共件」的维护成本。

教师实测证据见 `验证记录.md`，不能用预期值代替学生自己的实际结果。

## 十、排错

| 现象 | 先查什么 | 处理 |
| --- | --- | --- |
| 筛选后 `total` 不变 | `count()` 是否在 `filter` 之前 | 把过滤条件移到 `count()` 上方，用同一 `query` 计数与取页 |
| 过滤无命中返回 404 | service 是否把空结果当资源不存在 | 列表查不到是正常结果，返回 200 与空 `items`、`total=0` |
| `page=0` 返回 500 或 200 | 边界是否只写在 service | 在 `param.py` 用 `Field(ge=1, le=100)` 声明，由 FastAPI 返回 422 |
| 翻页出现重复或顺序不稳定 | 是否漏了 `order_by` | 固定 department `dept_code`、personnel `certificate_number` 后再分页 |
| `no such table: personnel` | personnel 模型是否在 `create_all` 前导入 | 在 `main.py` 导入 `personnel.model`，再执行 `create_all` |
| 启动报单位不存在或人员 seed 失败 | seed 顺序是否先单位后人员 | 先 `_seed_departments()`，再 `_seed_personnel()` |
| `?full_name=` 把全表筛空 | 空串是否被当成过滤值 | `if full_name:` 跳过空串；前端清空搜索时不传或传空串 |
| 新增人员返回 500 | 是否先校验所属单位 | service 先查 `dept_code`，不存在抛 400 |
| 422 与 400 混淆 | 错误产生位置 | 参数边界与字段格式是 422；重复证件号、单位不存在是 400 |
| 测试后仓库出现 `duty.db` | `DATABASE_URL` 是否在导入 `main` 前设置 | 在导入应用前指向临时目录；不要先导入再设环境变量 |
| 列表参数名与前端不一致 | 是否自造 `pageNum`、`size` | 全项目统一 `page`、`page_size`，过滤字段用列名 |

## 十一、提交

学生提交四项：

1. 代码：personnel 六文件；department 的 `param.py`、`crud.py`、`service.py`；`main.py` 的模型导入、路由挂载与 seed。
2. 根目录配置与说明：`README.md` 更新两个模块的路径、过滤参数与固定排序说明；`requirements.txt` 与 `.gitignore` 不变。
3. 回归记录：department 过滤命中/未命中、personnel 分页与过滤、`page=0` 422、两个模块的增删改查状态码；另附改造前后同一组请求的 `items`/`total` 对比。
4. 仓库卫生检查：`git status` 干净，`git ls-files` 不含 `venv/`、`.env`、`*.db`、`__pycache__/`。

提交前用 `git ls-files` 复核。教师完成态、`tests/`、难度评分与实测记录用于备课与验收，不代替学生操作。

## 十二、扩展

以下均为课后扩展，不占 90 分钟必做时间：

1. **多字段组合过滤（选做）**：同时传 `name=张&dept_code=D002`，验证两个条件都进入 `count()` 之前的同一 `query`；讨论「未筛选」与「筛选空值」的区别。
2. **分页边界（选做）**：验证 `page` 超过总页数返回空 `items` 与正确 `total`；讨论 `page_size` 上限为什么设 100。
3. **公共分页件（选做，教材 7.5）**：把「`count` + `offset` + `limit`」抽到 `app/core/pagination.py`，两个模块只负责设置查询，再跑同一组回归请求；比较与当前同构写法的取舍。
4. **排序白名单（选做，教材 7.4）**：为 department 增加 `sort_by` 白名单，比较固定键与白名单的适用场景；仍不把前端字符串直接拼进 `order_by`。
5. **索引依据**：personnel 的 `dept_code` 过滤可考虑索引；说明为什么 `certificate_number` 主键已有索引，而过滤列是否加索引要看数据量与查询比例。
6. **复习**：回看 6.2–6.4 与 7.1–7.5，指出哪些查询代码结构相同可收拢、哪些因带业务含义必须留在模块内。
