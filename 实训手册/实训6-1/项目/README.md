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

- `main.py`：创建应用、挂载模块路由、建表
- `app/core/database.py`：引擎、会话、`Base`、`get_db`
- `app/core/security.py`：密码哈希、令牌、当前用户依赖
- `app/modules/dept/`：第 5 章的单位模块，本章把 `model.py` 与 `crud.py` 换成数据库版（六文件齐备）
- `app/modules/user/`：本章的用户模块（model、schema、crud、service、controller）

## 配置

复制 `.env.example` 为 `.env`，按本机情况填写；`.env` 不纳入 Git。
`SECRET_KEY` 是令牌签名密钥，正式部署必须替换示例值。
