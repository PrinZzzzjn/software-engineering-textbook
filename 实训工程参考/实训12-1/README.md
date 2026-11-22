# 实训 12-1 模块测试与调试

本实训在实训 11-1 的完成态上正式引入 `tests/`：建立 `conftest.py` 夹具，写登录、单位重复、执勤首尾相接与时间重叠四条接口测试，并完成三处「改坏—变红—恢复」的定位训练。完成态见 `项目/`，学员起点见 `starter/`，实跑证据见 `验证记录.md`。本实训不新增业务接口，`app/` 与 `main.py` 保持 11-1 原样。

## 一、实训概览

| 项目 | 内容 |
| --- | --- |
| 对应教材 | 第 12 章 12.1–12.5 与「◆ 实训 12-1」 |
| 起点 | 实训 11-1 完成态：五个业务模块 + analytics + 三条执勤规则 |
| 完成态 | `tests/conftest.py` + `test_auth.py` + `test_department.py` + `test_duty.py`，5 条测试全绿 |
| 建议课时 | 4 学时，180 分钟（教材六步：20 + 30 + 50 + 30 + 30 + 20） |
| 难度 | D3 规模 / L3 认知，结论「合理」 |
| 必做 | 夹具、四条测试（正常/边界/异常）、连续两次一致、一处改坏定位 |
| 选做（课后） | 另外两处改坏、统计参数化、独立测试库、pre-commit |
| 教师验证 | `python -m pytest tests -q`，5 项全绿且连续两次一致；uvicorn 8019 的 11 项实测；三处改坏均被抓到 |
| 运行端口 | 文档与课堂演示用 8000；验证记录使用 8019 |

## 二、教学目标与教材映射

完成本实训后，学生应能：

1. 说明测试解决什么问题，并区分单元、接口、集成三层的成本与覆盖范围。
2. 用 pytest 与 TestClient 写出第一条接口测试，会运行、会读通过和失败。
3. 用 fixture 准备客户端与令牌，为正常、边界、异常三类路径各写用例。
4. 用 uuid 与靠后的随机日期让测试数据可重复，连续运行两次结果一致。
5. 按「实际 == 期望」读失败信息，先判断代码 bug 还是测试写错，再按状态码定位。

| 教材位置 | 内容 | 本实训落点 |
| --- | --- | --- |
| 12.1 | 测试的作用与限度、回归缺陷 | README 3.1 与实训小结 |
| 12.2 | 单元 / 接口 / 集成三层 | README 3.1 分层表；本章只做接口测试 |
| 代码 12-2-1 | 纯函数单元测试的形状 | README 3.1 说明「本章不改造重叠函数」 |
| 12.3 | pytest 发现规则、`pip install pytest httpx` | README 第八节与分步指南阶段 1 |
| 代码 12-3-1 | `tests/conftest.py` 三个夹具 | `tests/conftest.py` |
| 代码 12-3-2 / 12-3-3 / 12-3-4 | 第一条测试、通过、失败输出 | `test_login_success` 与分步指南阶段 1 |
| 12.4 | 三类路径、一个测试一个行为 | README 3.2 与四条测试 |
| 代码 12-4-1 / 12-4-2 / 12-4-3 | 登录失败、单位重复、首尾相接 | `test_auth.py`、`test_department.py`、`test_duty.py` |
| 12.4 | 测试数据可重复的三种做法 | README 3.3；教师版采用独立测试库 |
| 12.5 | 失败信息读法与状态码定位表 | README 3.4 |
| 12.5 | 三处改坏 | 分步指南阶段 4–5 与 `验证记录.md` |
| 例 12-1 / 代码 12-5-1 | 执勤时间重叠返回 400 | `test_duty_record_overlap` |
| 例 12-2 / 代码 12-5-2 | 读一条失败信息 | 分步指南阶段 4 的定位记录模板 |
| 实训 12-1 步骤 1–6 | 跑起来、登录、单位与执勤、改坏、找 bug、提交 | 分步指南阶段 1–6 |

## 三、边界与不变量

### 3.1 三层的区别

| 类型 | 测什么 | 本章例子 | 成本 | 本实训是否做 |
| --- | --- | --- | --- | --- |
| 单元测试 | 一个函数或一段纯逻辑 | 时间重叠判断 `is_overlap` | 低，运行快 | 否；教材明确「本章不要求做这次改造」 |
| 接口测试 | 一个 HTTP 接口的输入与输出 | 登录 200/401、单位重复 400 | 中，需要客户端与数据 | **是，本章主体** |
| 集成测试 | 多个部件连在一起 | 登录 → 建单位 → 查列表 | 高，失败难定位 | 否；留第 13 章联调 |

### 3.2 四条测试与三类路径

| 文件 | 用例 | 路径 | 期望 |
| --- | --- | --- | --- |
| `test_auth.py` | `test_login_success` | 正常 | 200，含 `access_token` |
| `test_auth.py` | `test_login_wrong_password` | 异常 | 401 |
| `test_department.py` | `test_create_department_duplicate` | 异常 | 第一次 201，第二次 400 |
| `test_duty.py` | `test_duty_record_touching` | 边界 | 两条都 201（12:00 首尾相接） |
| `test_duty.py` | `test_duty_record_overlap` | 异常（例 12-1） | 第一条 201，第二条 400 |

一个测试只验一个行为；准备数据时的 `assert 201` 是准备断言，不是验证目标。`test_create_department_duplicate` 的第一次 201 与 `test_duty_record_*` 的第一条 201 都属于此类：准备失败时测试立刻变红，避免把「数据没准备好」误判成「规则生效」。

### 3.3 测试数据可重复

- 单位编码用 `uuid.uuid4().hex[:6]`，每次不同，不会与上次运行留下的数据冲突。
- 执勤日期用 `date.today() + timedelta(days=random.randint(1000, 2000))`，落在 2029 年以后，避开种子数据。
- 连续运行两次必须都是 5 passed；「第一次通过、第二次失败」不是代码坏了，而是测试没有隔离。
- 教材把「独立测试库」列为课后扩展；教师版在 `conftest.py` 导入 `main` 之前把 `DATABASE_URL` 指向系统临时目录，测试结束删除，仓库不生成 `duty.db`。学员版按教材直接使用项目库即可。

### 3.4 失败定位四步

先看状态码，再看 `detail`，再看 `/docs` 里的契约，最后才改代码。

| 状态码 | 先查什么 |
| --- | --- |
| 422 | 请求体字段名、类型、必填 |
| 400 | 业务规则：重复、时间冲突、人员不存在 |
| 401 | 密码、令牌、请求头 |
| 500 | 日志或堆栈：字段名、表名、空值 |

记录表固定五栏：现象、实际值、期望值、判断（代码 bug / 测试写错）、处理。

### 3.5 其他不变量

- 本实训不新增、不修改业务接口；`app/`、`main.py`、`requirements.txt` 与 11-1 相同，版本仍为 0.3.0。
- `tests/` 从本章起成为工程正式组成部分，与代码同仓提交；文件名与函数名都以 `test_` 开头。
- `conftest.py` 的 `seed_admin` 用 `scope="session", autouse=True`，整轮测试只建一次管理员，且与接口读同一个库。
- 认证仍为 hashlib 盐哈希 + `TOKEN_STORE`，不引入 JWT、passlib、python-jose。
- `from main import app` 要求在项目根目录用 `python -m pytest` 运行；直接在 `tests/` 里运行会报 `ModuleNotFoundError: No module named 'main'`。
- 教材 12.5 的「改坏 3」指向 `service.py` 的 `create_duty_record()`；本工程按第 4 章六文件分工把范围查询放在 `app/modules/duty_record/crud.py::find_overlap`，条件与语义完全相同，改坏位置以本工程文件为准。

## 四、课前准备

- 11-1 完成态工程（或直接用 `starter/`）。
- 已安装 pytest 与 httpx：`python -m pip install pytest httpx`。
- 起点自带的 `P001`、`W001` 与 `admin/admin123`（`main.py` 导入时幂等 seed）。
- 一张失败定位记录表（现象、实际值、期望值、判断、处理）。

## 五、时间安排（180 分钟）

| 阶段 | 内容 | 教材步骤 | 预算 |
| --- | --- | --- | ---: |
| 0 | 起点检查、确认 `tests/` 为空 | — | 5 |
| 1 | 建 `conftest.py` 与登录成功测试 | 步骤 1 | 20 |
| 2 | 补登录失败测试 | 步骤 2 | 30 |
| 3 | 单位重复与执勤首尾相接 | 步骤 3 | 50 |
| 4 | 故意改坏一处并定位 | 步骤 4 | 30 |
| 5 | 另外两处找 bug 活动 | 步骤 5 | 30 |
| 6 | 提交与小结 | 步骤 6 | 20 |
| 合计 | | | **185**（含阶段 0 的 5 分钟机动） |

教材六步合计 180 分钟；阶段 0 的 5 分钟从阶段 6 的小结中调剂。

## 六、操作步骤

1. **跑起来（20 分钟）**：建 `tests/conftest.py` 与 `tests/test_auth.py`，在项目根目录运行 `python -m pytest -q`，应看到 `1 passed`。
2. **登录失败（30 分钟）**：补 `test_login_wrong_password`，运行 `python -m pytest -q tests/test_auth.py`，应看到 `2 passed`。
3. **单位与执勤（50 分钟）**：新建 `test_department.py` 与 `test_duty.py`，用 uuid 与随机日期；运行两次，均应 `5 passed`。
4. **故意改坏（30 分钟）**：从三处改法选一处，改坏、运行对应文件、填五栏记录、恢复并重跑。
5. **找 bug 活动（30 分钟）**：另外两处各独立做一遍；一次只改一处。
6. **提交与小结（20 分钟）**：运行全量测试，用三句话说清「写了哪四条、覆盖哪三类、抓到过什么」。

详细代码与改坏步骤见 [分步实现指南.md](分步实现指南.md)。

## 七、文件清单

新增：

```text
tests/conftest.py        # 夹具：seed_admin、client、admin_headers；约 60 行
tests/test_auth.py       # 登录成功、登录失败；2 条
tests/test_department.py # 单位编码重复；1 条
tests/test_duty.py       # 首尾相接、时间重叠；2 条
```

修改：

```text
README.md（项目内）       # 测试目录、运行方式与验证说明
```

未改：`main.py`、`app/` 全部模块、`requirements.txt`、`.env.example`、`.gitignore`。本实训不新增业务代码。

## 八、快速开始

```powershell
cd 项目
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pytest httpx
python -m pytest -q
python -m uvicorn main:app --port 8000
```

`python -m pytest -q` 的末尾应为 `5 passed`。测试默认把数据库指向系统临时目录（教师版增强），项目根目录不会生成 `duty.db`。启动服务后可在 `/docs` 复核被测接口：`POST /users/login`、`POST /departments`、`POST /duty-records`。

## 九、验收标准

| 验收项 | 判定方式 |
| --- | --- |
| 三层区别能说明 | 能各举一例，说明成本与覆盖范围的交换，并指出本章写的是接口层 |
| 四条测试可运行 | `python -m pytest -q` 至少 4 passed（含例 12-1 为 5 passed） |
| 连续两次一致 | 连续运行两次结果相同，不依赖上次留下的数据 |
| 三类路径覆盖 | 正常、边界、异常各至少一条 |
| 失败可定位 | 至少一次故意失败，五栏记录能复述「实际、期望、判断、处理」 |
| 改坏能被抓到 | 三处改坏分别使对应文件变红，恢复后重新变绿 |
| 回归与卫生 | 11-1 的业务行为不变；无 `duty.db`、`venv/`、`__pycache__/`、`.pytest_cache/` |

## 十、常见问题与排错

| 现象 | 先查什么 |
| --- | --- |
| `ModuleNotFoundError: No module named 'main'` | 是否在项目根目录用 `python -m pytest` 运行 |
| 一运行就 401 | `conftest.py` 是否被加载；`seed_admin` 是否建了管理员；请求头是否带令牌 |
| 单位测试第一次就 400 | 编码写死，或 uuid 没有生效 |
| 执勤第一条 400 | `P001`、`W001` 是否存在（`main.py` 的 seed 是否执行） |
| 执勤第二条 400 | 日期不是每次不同，或重叠条件写成 `>=` |
| 执勤测试返回 404 | `main.py` 是否挂载 `duty_record` 路由，前缀是否为 `/duty-records` |
| 测试互相影响 | 共享数据未隔离；单位编码与执勤日期是否每次不同 |
| 偶发失败 | 日期或随机数是否固定；两次运行是否撞到同一天 |
| 断言太宽 | 只断言状态码，未检查 `access_token` 等关键字段 |

## 十一、提交要求

提交 `tests/` 与一份失败定位记录。记录至少包含：

- 三处改坏中至少一处的五栏记录：现象、实际值、期望值、判断、处理；
- 改坏前后的 pytest 输出（哪一条红、哪一条绿）；
- `python -m pytest -q` 连续两次的实际结果；
- 四条测试分别覆盖哪一类路径的对照表。

## 十二、课后扩展

1. 把另外两处改坏各自独立做一遍，补齐三份定位记录。
2. 为统计模块补参数化用例：非法年份 `26`、`20261`、`abcd` 都返回 400。
3. 改用独立测试库（教师版 `conftest.py` 已示范），让测试不碰开发数据。
4. 把测试接入提交前检查（pre-commit 或脚本），提交前自动运行。
5. 写一条「测试本身写错」的排查记录，说明如何从 `actual == expected` 判断是期望写错。
6. **复习任务**：回看第 3 章 3.5（Pydantic）与 3.6（`HTTPException`）、第 4 章 4.5（`Depends`）、第 10 章 10.3（业务规则的归属），说明 fixture、断言与失败信息分别解决测试中的哪一步问题。
