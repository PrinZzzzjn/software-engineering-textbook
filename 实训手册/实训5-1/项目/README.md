# Duty API

## 启动

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

访问 `http://127.0.0.1:8000/health` 与 `http://127.0.0.1:8000/docs`。

## 目录

- `main.py`：创建应用、挂路由
- `app/modules/dept/`：六文件模块（`controller.py`、`service.py`、`crud.py`、`model.py`、`schema.py`、`param.py`）

## 按需加入的文件

- 第 6 章：`app/core/database.py`、`security.py`，以及 `main.py` 的建表三行
- 第 12 章：`tests/`

## 配置

复制 `.env.example` 为 `.env`，按本机情况填写；`.env` 不纳入 Git。
