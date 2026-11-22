# 实训 13-1 完成态项目

本项目从实训 12-1 的测试工程演进而来：接口路径、字段与状态码不变，12-1 的 5 条测试原样保留；新增的是第 13 章要求的质量改造、事务边界、12 步联调用例与四份交付文档。应用版本从 0.3.0 升到 0.4.0。

## 启动

要求 Python 3.10 及以上。在本目录执行：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pytest httpx
python -m uvicorn main:app --port 8000
```

浏览器打开 <http://127.0.0.1:8000/docs>。业务路径为 `/departments`、`/personnel`、`/workstations`、`/duty-records`、`/analytics` 与 `/users`，不使用版本化前缀。`GET /health` 返回 `{"status": "healthy"}`。

## 目录

```text
项目/
├── main.py                  # 应用装配、建表、幂等 seed
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── 问题清单.md              # 五类问题：位置、修复动作、验证方式
├── 联调记录.md              # 教材 13.4 的 12 步：请求、期望、实际、结论
├── 交付清单.md              # 五项交付物与证据
├── 已知问题.md              # 按阻断上线 / 影响体验 / 可延后分级
├── app/
│   ├── core/
│   │   ├── database.py      # engine、SessionLocal、Base、get_db、commit_or_rollback
│   │   ├── pagination.py    # 13-1 新增：公共分页 paginate
│   │   └── security.py      # 盐哈希、令牌、认证与授权依赖
│   └── modules/
│       ├── department/      # 六文件；列表挂输出模型
│       ├── personnel/       # 六文件；列表挂输出模型
│       ├── workstation/     # 六文件；列表挂输出模型
│       ├── duty_record/     # 六文件；批量入口 + 三条业务规则
│       ├── analytics/       # 只读统计
│       └── user/            # 六文件；账号管理
└── tests/
    ├── conftest.py          # seed_admin、client、admin_headers、normal_headers、db_session
    ├── test_auth.py         # 12-1 原样：登录成功、登录失败
    ├── test_department.py   # 12-1 原样：单位编码重复
    ├── test_duty.py         # 12-1 原样：首尾相接、时间重叠
    ├── test_integration.py  # 13-1 新增：13.4 的 12 步联调
    └── test_quality.py      # 13-1 新增：安全、错误、规范、事务
```

## 13-1 改了什么

| 类别 | 问题 | 位置 | 修复 |
| --- | --- | --- | --- |
| 安全 | 列表直接返回 ORM 对象，新增敏感字段就会泄露 | 五个 `controller.py` 的 `GET` 列表 | 增加 `*ListOut` 输出模型，字段白名单化 |
| 错误 | `commit()` 分散在 CRUD，异常路径没有 `rollback()` | 各模块 `crud.py` | 统一走 `app/core/database.py::commit_or_rollback` |
| 错误 | 请求级会话异常后可能停在失败事务里 | `app/core/database.py::get_db` | 捕获异常先 `rollback()` 再向上抛 |
| 重复 | 五个模块各写一遍“计数 + 取页” | department / personnel / workstation / duty_record / user 的 `crud.list_page` | 收拢到 `app/core/pagination.py::paginate` |
| 性能 | 重叠判断把整段冲突记录搬到内存 | `duty_record/crud.py::find_overlap` | 只需要“是否存在”，改用 `.first()` |
| 规范 | 删除用户模块未使用的 `list_all` | `user/crud.py` | 删除死代码 |
| 规范 | 批量写入没有可验证的事务入口 | `duty_record/service.py` | 新增 `create_duty_records`，单条创建复用它 |

接口契约不变：路径、请求字段、响应结构、状态码与 12-1 完全一致；列表仍返回 `{items, total}`，只是现在由输出模型裁剪。

## 事务边界

- 一个业务动作一个事务：`crud` 里先 `add` / 修改，最后调用一次 `commit_or_rollback`。
- `commit` 失败时先 `db.rollback()`，再把异常继续抛出，由框架转成 500；不吞异常假装成功。
- `get_db` 在请求异常时也回滚，避免会话停在失败事务里。
- 只读接口（列表、详情、统计）不提交事务。
- `service.create_duty_records` 先逐条校验、再检查批内重叠、最后一次性写入；任何一条不通过都在 `add` 之前抛出，数据库不会留下半批数据。

## 测试

在项目根目录执行：

```powershell
python -m pytest -q
```

27 条用例：

| 文件 | 条数 | 覆盖 |
| --- | ---: | --- |
| `test_auth.py` | 2 | 登录成功、登录失败（12-1 原样） |
| `test_department.py` | 1 | 单位编码重复（12-1 原样） |
| `test_duty.py` | 2 | 首尾相接、时间重叠（12-1 原样） |
| `test_integration.py` | 12 | 13.4 的 12 步主链路联调 |
| `test_quality.py` | 10 | 响应不泄露密码；400/401/403/404/422；列表结构一致；批量写入的原子性、批内重叠 |

`tests/conftest.py` 在导入 `main` 之前把 `DATABASE_URL` 指向系统临时目录，整轮测试结束删除；项目根目录不会生成 `duty.db`。

## 交付材料

| 文件 | 内容 |
| --- | --- |
| [问题清单.md](问题清单.md) | 五类问题各至少一条，位置精确到文件与函数，附验证方式 |
| [联调记录.md](联调记录.md) | 12 步联调：请求、期望、实际、结论、失败原因 |
| [交付清单.md](交付清单.md) | 代码与提交记录、接口文档、可运行测试、工作清单、已知问题 |
| [已知问题.md](已知问题.md) | 遗留问题分级与处理建议 |

## 已知问题摘要

- 统计分析在 Python 内聚合，数据量很大时应下推为 SQL 聚合（可延后）。
- 令牌存进程内字典，重启失效，多进程部署不共享（可延后；教材 8 章的既定设计）。
- 删除单位不检查是否被人员或哨位引用，可能留下悬空 `dept_code`（影响体验）。
- 批量入口只被单条接口与测试使用，尚未开放 HTTP 端点（可延后）。

完整分级见 [已知问题.md](已知问题.md)。

## 与 12-1 的兼容

- 12-1 的 5 条测试逐字保留，仍全部通过。
- 路径、字段、状态码、权限矩阵不变；前端与后续章节的调用方式不变。
- 运行依赖不变（fastapi、uvicorn、sqlalchemy）；pytest 与 httpx 仍为开发依赖。
- 旧库可直接启动，无表结构迁移；只新增了 `app/core/pagination.py` 与两个测试文件。
