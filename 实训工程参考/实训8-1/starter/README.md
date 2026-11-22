# 实训 7-1 完成态项目

这是从实训 6-1 数据库版单位模块演进到「单位 + 人员」两个模块的完成态。两个模块共用同一套查询写法：分页参数收进 `param.py`，过滤条件在 `crud.py` 中先拼装、后计数，列表固定排序并返回 `{items, total}`。数据写入项目根目录的 `duty.db`，启动时自动建表并幂等写入 D001、D002 与 P001、P002。

## 启动

要求 Python 3.10 及以上。在本目录执行：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

若 PowerShell 不允许激活脚本，可不激活，直接执行 `.\venv\Scripts\python.exe -m pip ...` 与 `.\venv\Scripts\python.exe -m uvicorn ...`。Linux/macOS 使用 `source venv/bin/activate`。

浏览器打开 <http://127.0.0.1:8000/docs>。`GET /health` 返回 `{"status": "healthy"}`，业务路径为 `/departments` 与 `/personnel`，不使用版本化前缀。停止服务按 `Ctrl+C`。

## 目录

```text
项目/
├── main.py                  # 创建应用、健康检查、挂两个路由、建表、幂等 seed
├── requirements.txt         # 运行依赖：fastapi、uvicorn、sqlalchemy
├── .env.example             # 配置变量示例；DATABASE_URL 由环境变量提供
├── .gitignore               # 排除环境、密钥、SQLite 数据库与缓存
├── README.md
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── database.py      # engine、SessionLocal、Base、get_db
│   └── modules/
│       ├── __init__.py
│       ├── department/      # 六文件：controller/service/crud/model/schema/param
│       └── personnel/       # 六文件，写法与 department 同构
└── tests/
    └── test_api.py          # 教师验证用；第 12 章才系统讲测试
```

## 数据库与配置

- 数据库地址从环境变量 `DATABASE_URL` 读取，未设置时回落到本目录的 `duty.db`（`sqlite:///./duty.db`）。
- 本章不引入 `python-dotenv`，`.env` 不会被自动加载；需要改库时在启动前设置系统环境变量。
- `*.db` 与 `*.db-journal` 已被 `.gitignore` 排除，运行数据不进入仓库。
- 删除 `duty.db` 后重启即可回到只有 D001、D002 与 P001、P002 的初始状态。

## 接口

| 方法 | 路径 | 成功 | 失败 |
| --- | --- | --- | --- |
| GET | `/departments?page=1&page_size=10&full_name=一` | 200，`{items, total}` | 422 |
| POST | `/departments` | 201 | 400（编码重复）、422 |
| GET | `/departments/{dept_code}` | 200 | 404 |
| PUT | `/departments/{dept_code}` | 200 | 404、422 |
| DELETE | `/departments/{dept_code}` | 204，无正文 | 404 |
| GET | `/personnel?page=1&page_size=10&name=张&dept_code=D001` | 200，`{items, total}` | 422 |
| POST | `/personnel` | 201 | 400（证件号重复或单位不存在）、422 |
| GET | `/personnel/{certificate_number}` | 200 | 404 |
| PUT | `/personnel/{certificate_number}` | 200 | 400（单位不存在）、404、422 |
| DELETE | `/personnel/{certificate_number}` | 204，无正文 | 404 |

列表规则：

- `page` 默认 1、`page_size` 默认 10 且上限 100；`page=0`、`page_size=0` 由参数模型返回 422。
- department 按 `full_name` 模糊过滤；personnel 按 `name` 模糊、`dept_code` 精确过滤；空串视为不筛选。
- 过滤条件先于 `count()`，`total` 是过滤后的总数；过滤无命中返回 200、`items: []`、`total: 0`。
- 排序由后端固定：department 按 `dept_code` 升序，personnel 按 `certificate_number` 升序；前端不传 `sort_by`。

## 教师验证

在实训根目录执行（测试会把数据库指向系统临时目录，不在仓库生成 `duty.db`）：

```powershell
python -m pytest 项目\tests -q
```

`tests/` 只用于教师实跑验证，学生本实训不必编写测试；教材第 12 章才正式引入测试。
