# Duty API

## 启动

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

访问 `http://127.0.0.1:8000/health` 与 `http://127.0.0.1:8000/docs`。首次启动会生成 `duty.db`。

## 目录

- `main.py`：创建应用、挂载模块路由、导入模型并调用 `create_all` 建表
- `app/core/database.py`：`engine`、`SessionLocal`、`Base`、`get_db`（第 6 章建立）
- `app/core/security.py`：密码哈希、令牌、当前用户依赖
- `app/modules/department/`：单位模块（六文件，落库版）
- `app/modules/user/`：用户模块（model、schema、crud、service、controller，落库版）

`departments` 与 `users` 两张表都在 `duty.db` 里；重启后记录仍在，令牌字典 `TOKEN_STORE` 会清空，需要重新登录。

## 配置

`.env.example` 含 `DEBUG` 与 `DATABASE_URL`，按需复制为 `.env`；`.env` 与 `*.db` 均不纳入 Git。
