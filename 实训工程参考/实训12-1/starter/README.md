# 实训 12-1 起点项目

本项目是实训 11-1 的完成态，作为 12-1 的起点。业务代码与 11-1 相同：五个业务模块、analytics 统计、三条执勤规则；`main.py` 幂等 seed `P001`、`W001` 与 `admin/admin123`。

本目录**不含** `tests/`，第 12 章从零建立测试目录。起点说明与预置数据见 [起点说明.md](起点说明.md)。

## 启动

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pytest httpx
python -m uvicorn main:app --port 8000
```

浏览器打开 <http://127.0.0.1:8000/docs>。业务路径为 `/departments`、`/personnel`、`/workstations`、`/duty-records`、`/analytics` 与 `/users`，不使用版本化前缀。

## 主要接口

| 方法 | 路径 | 权限 |
| --- | --- | --- |
| POST | `/users/login` | 公开 |
| GET/POST/PUT/DELETE | `/departments`、`/personnel`、`/workstations` | 读公开，写管理员 |
| GET/POST/DELETE | `/duty-records` | 读公开，写管理员 |
| GET | `/analytics/staff-duty-yearly`、`/analytics/duty-time-distribution` | 公开 |

完整字段、状态码与规则见 `../README.md` 与 `../接缝表.md`。
