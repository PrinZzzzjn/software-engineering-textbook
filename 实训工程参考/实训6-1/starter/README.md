# 实训 5-1 完成态项目

这是从综合实训 4-1 逐字迁移的单位六文件内存版，并补齐工程入口、依赖、配置示例与忽略规则。数据只保存在当前进程，重启后清空；本阶段没有数据库、认证、`app/core/` 或 `tests/`。

## 启动

要求 Python 3.10 及以上。在本目录执行：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

若 PowerShell 不允许激活脚本，可不激活，直接执行 `.\venv\Scripts\python.exe -m pip ...` 与 `.\venv\Scripts\python.exe -m uvicorn ...`。Linux/macOS 使用 `source venv/bin/activate`。

浏览器打开 <http://127.0.0.1:8000/docs>。`GET /health` 返回 `{"status": "healthy"}`，业务路径为 `/departments` 与 `/departments/{dept_code}`，没有 `/api/v1` 前缀。停止服务按 `Ctrl+C`。

## 目录

```text
项目/
├── main.py                  # 创建应用、健康检查、挂路由
├── requirements.txt         # 运行依赖：fastapi、uvicorn
├── .env.example             # 配置变量示例；本阶段只列 DEBUG
├── .gitignore               # 排除环境、密钥、数据库、日志和缓存
├── README.md
└── app/
    ├── __init__.py
    └── modules/
        ├── __init__.py
        └── department/
            ├── __init__.py
            ├── controller.py
            ├── service.py
            ├── crud.py
            ├── model.py
            ├── schema.py
            └── param.py
```

## 配置与验证

复制 `.env.example` 为 `.env` 后可填写本机值，`.env` 不得提交。本章只学习配置外置，应用尚未读取 `DEBUG`，因此不引入额外配置库；数据库地址到第 6 章才加入。

教师可在激活的虚拟环境中另装 `httpx`、`pytest`，然后从本目录运行 `python ..\verify_api.py`。该脚本位于实训根目录，不在项目中建立 `tests/`。
