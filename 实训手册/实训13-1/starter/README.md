# 实训 13-1 起点项目

本项目是 **实训 12-1 的完成态**，作为 13-1 的起点。业务代码、接口契约与 12-1 相同，`tests/` 已有 5 条接口测试并全部通过；本实训在此基础上做质量改造、事务收拢与主链路联调。

起点**没有** `问题清单.md`、`联调记录.md`、`交付清单.md`、`已知问题.md`，也没有 `app/core/pagination.py` 与批量写入入口——这些正是 13-1 要补的内容。

起点说明与验收入口见 [起点说明.md](起点说明.md)。

## 启动

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pytest httpx
python -m uvicorn main:app --port 8000
```

浏览器打开 <http://127.0.0.1:8000/docs>。业务路径为 `/departments`、`/personnel`、`/workstations`、`/duty-records`、`/analytics` 与 `/users`。

## 基线测试

```powershell
python -m pytest -q
```

预期 `5 passed`。这 5 条断言在 13-1 中不得改坏，改造后必须仍然通过。

## 主要接口

| 方法 | 路径 | 权限 |
| --- | --- | --- |
| POST | `/users/login` | 公开 |
| GET/POST/PUT/DELETE | `/departments`、`/personnel`、`/workstations` | 读公开，写管理员 |
| GET/POST/DELETE | `/duty-records` | 读公开，写管理员 |
| GET | `/analytics/staff-duty-yearly`、`/analytics/duty-time-distribution` | 公开 |
