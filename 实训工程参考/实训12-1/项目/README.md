# 实训 12-1 完成态项目

本项目从实训 11-1 的统计工程演进而来，业务代码保持不变，新增正式的 `tests/`：`conftest.py` 夹具与五条接口测试（教材四条必做 + 例 12-1）。账号仍写入 `duty.db`（测试时由夹具指向系统临时目录），令牌仍登记在进程内字典 `TOKEN_STORE`，重启后旧令牌失效。

## 启动

要求 Python 3.10 及以上。在本目录执行：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

浏览器打开 <http://127.0.0.1:8000/docs>。业务路径为 `/departments`、`/personnel`、`/workstations`、`/duty-records` 与 `/users`，不使用版本化前缀。`GET /health` 返回 `{"status": "healthy"}`。

## 目录

```text
项目/
├── main.py                  # 应用装配、建表、幂等 seed（含哨位与执勤记录）
├── requirements.txt         # 运行依赖：fastapi、uvicorn、sqlalchemy
├── .env.example
├── .gitignore
├── README.md
├── app/
│   ├── core/
│   │   ├── database.py      # engine、SessionLocal、Base、get_db
│   │   └── security.py      # 盐哈希、令牌、get_current_user、get_current_admin_user
│   └── modules/
│       ├── department/      # 六文件；写接口挂管理员依赖
│       ├── personnel/       # 六文件；写接口挂管理员依赖
│       ├── workstation/     # 六文件；10-1 新增，写接口挂管理员依赖
│       ├── duty_record/     # 六文件；三条业务规则在 service
│       ├── analytics/       # 11-1 新增：schema + service + controller，只读统计
│       └── user/            # 六文件；账号管理
└── tests/
    ├── conftest.py          # seed_admin、client、admin_headers
    ├── test_auth.py         # 登录成功、登录失败
    ├── test_department.py   # 单位编码重复
    └── test_duty.py         # 首尾相接、时间重叠
```

## 数据库与配置

- 数据库地址从环境变量 `DATABASE_URL` 读取，未设置时回落到本目录的 `duty.db`。
- 启动时 `create_all` 只在缺失时建表；旧库已有 `departments`、`personnel`、`users` 时不会清空数据，新表 `workstations`、`duty_records` 会自动补建。
- 删除 `duty.db` 后重启即可回到初始状态：D001/D002、P001/P002、W001/W002 与四条 2026 年执勤记录，以及 `admin/admin123`。
- `*.db`、`.env`、`venv/`、`__pycache__/` 均已被 `.gitignore` 排除。

## 新增模块与接口

### 哨位 `/workstations`

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| GET | `/workstations` | 公开 | `?page=1&page_size=10&dept_code=`，返回 `{items, total}` |
| POST | `/workstations` | 管理员 | 201；编号重复 400「哨位编号已存在」；单位不存在 400「所属单位不存在」 |
| GET | `/workstations/{workstation_id}` | 公开 | 200 / 404 |
| PUT | `/workstations/{workstation_id}` | 管理员 | 200 / 404 / 422 |
| DELETE | `/workstations/{workstation_id}` | 管理员 | 204 / 404 |

字段：`workstation_id`、`name`、`dept_code`、`is_active`（0/1，默认 1）。

### 执勤记录 `/duty-records`

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| GET | `/duty-records` | 公开 | `?page=1&page_size=10&personnel_certificate_number=&workstation_id=` |
| POST | `/duty-records` | 管理员 | 201；三条业务规则失败均为 400 |
| GET | `/duty-records/{record_id}` | 公开 | 200 / 404 |
| DELETE | `/duty-records/{record_id}` | 管理员 | 204 / 404 |

没有 PUT（更新）接口，与 `项目参考/duty-simplified/` 的接口契约一致。

字段：`id`、`personnel_certificate_number`、`workstation_id`、`start_time`、`end_time`、`status`（默认 `normal`）。

## 三条业务规则与校验顺序

规则集中在 `app/modules/duty_record/service.py` 的 `_validate_duty_record`，顺序固定为「先便宜、后昂贵」：

| 顺序 | 规则 | 范围类型 | 失败状态与提示 | 是否查库 |
| ---: | --- | --- | --- | --- |
| 1 | 开始时间早于结束时间 | 跨字段 | 400「开始时间必须早于结束时间」 | 否 |
| 2 | 人员必须存在 | 跨表 | 400「人员不存在」 | 1 次 |
| 3 | 哨位必须存在 | 跨表 | 400「哨位不存在」 | 1 次 |
| 4 | 同一哨位时间不重叠 | 跨记录 | 400「该哨位在该时段已有执勤安排」 | 1 次范围查询 |

- 重叠条件是 `已有开始 < 新结束 且 已有结束 > 新开始`；首尾相接（08:00–12:00 之后接 12:00–14:00）不算冲突。
- 全部校验通过后才调用 `crud.create`；校验过程中不 `commit`，失败后数据库没有半条记录。
- 参数格式错误由 Pydantic 返回 422，先于业务规则；记录不存在返回 404。

## 统计分析 `/analytics`（只读）

按教材 11.2 的模块划分，`analytics` 没有 `model.py` 与 `crud.py`，只有 `schema.py`、`service.py`、`controller.py`；它直接读取 `DutyRecord` 与 `Personnel` 的模型，不写回任何表。

| 方法 | 路径 | 权限 | 参数 | 说明 |
| --- | --- | --- | --- | --- |
| GET | `/analytics/staff-duty-yearly` | 公开 | `personnel_certificate_number`、`year` | 年度总天数、总时长、12 个月分布 |
| GET | `/analytics/duty-time-distribution` | 公开 | 同上 | 24 小时分布、高峰时段、记录数 |

输入检查顺序：年份必须 4 位数字（否则 400「年份格式错误」）→ 人员必须存在（否则 400「人员不存在」）→ 查记录。人员存在但没有记录属于合法输入，返回 0 与补齐的 0 列表，不报错。

### 口径

| 指标 | 规则（含边界） | 计量单位 |
| --- | --- | --- |
| 总执勤天数 | 按自然日去重；开始日到结束日每个日期都算，结束日为次日 00:00 也算一天；年份按 `start_time` 判定 | 天 |
| 总执勤时长 | 每条「结束减开始」后累加，保留两位小数 | 小时 |
| 月度分布 | 固定 12 项；按 `start_time` 的月份归月，跨月记录的全部日期都记在开始月 | 天、小时 |
| 时段分布 | 固定 24 项；按 `start_time` 的小时计数，无记录补 0 | 条 |
| 高峰时段 | 返回所有达到最大计数的小时；无记录时为空列表 | 小时 |

对账关系：总天数 = 各月天数之和；总时长 = 各月时长之和。任何一条对不上，先查口径，不要先改代码。

统计接口只读，不调用 `db.commit()`，也不需要事务；只有写汇总表或批量导入时才需要「要么全成功、要么全回滚」。本工程不建汇总表，课后扩展可以练习。

## 权限矩阵

| 端点 | 匿名 | 普通用户 | 管理员 |
| --- | --- | --- | --- |
| `GET /health` | 200 | 200 | 200 |
| `POST /users`（注册） | 201 | 201 | 201 |
| `POST /users/login` | 200 / 401 / 422 | 200 / 401 / 422 | 200 / 401 / 422 |
| `GET /users/me` | 401 | 200 | 200 |
| `GET /users` | 401 | 403 | 200 |
| `PUT /users/{user_id}` | 401 | 403 | 200 / 400 / 404 / 422 |
| `GET /departments`、`GET /departments/{code}` | 200 / 404 | 200 / 404 | 200 / 404 |
| `POST/PUT/DELETE /departments` | 401 | 403 | 201 / 200 / 204 |
| `GET /personnel`、`GET /personnel/{number}` | 200 / 404 | 200 / 404 | 200 / 404 |
| `POST/PUT/DELETE /personnel` | 401 | 403 | 201 / 200 / 204 |
| `GET /workstations`、`GET /workstations/{id}` | 200 / 404 | 200 / 404 | 200 / 404 |
| `POST/PUT/DELETE /workstations` | 401 | 403 | 201 / 200 / 204 |
| `GET /duty-records`、`GET /duty-records/{id}` | 200 / 404 | 200 / 404 | 200 / 404 |
| `POST/DELETE /duty-records` | 401 | 403 | 201 / 204 |
| `GET /analytics/staff-duty-yearly` | 200 / 400 / 422 | 200 / 400 / 422 | 200 / 400 / 422 |
| `GET /analytics/duty-time-distribution` | 200 / 400 / 422 | 200 / 400 / 422 | 200 / 400 / 422 |

写接口一律管理员、读接口保持公开，与 9-1 的口径一致。执勤记录包含人员与时间信息，但教材 10-1 未要求收紧读权限，因此列表与详情仍公开；如需限制，属于课后扩展。

## 与 9-1 的兼容

- users 的注册、登录、`me`、列表、修改契约不变。
- department、personnel 的路径、字段、分页、过滤、排序、400/404/422 文案不变；写操作仍要求管理员。
- 运行依赖、`.env.example`、`.gitignore` 与 9-1 完全相同，没有新增依赖。
- 旧库可直接启动：`create_all` 只补建 `workstations` 与 `duty_records`。

## 教师验证

在 `项目/` 目录执行：

```powershell
python -m pip install pytest httpx
python -m pytest -q
```

5 条接口测试覆盖正常、边界、异常三类路径：登录成功（200）、登录失败（401）、单位编码重复（201 → 400）、执勤首尾相接（两条都 201）、执勤时间重叠（201 → 400）。单位编码用 uuid、执勤日期用靠后的随机日期，连续两次运行结果一致。

`tests/conftest.py` 与教材代码 12-3-1 相同；教师版额外在导入 `main` 之前把 `DATABASE_URL` 指向系统临时目录，测试结束删除，项目根目录不生成 `duty.db`（对应教材 12.4「独立测试库」的课后扩展）。详细实测见 `../验证记录.md`。
