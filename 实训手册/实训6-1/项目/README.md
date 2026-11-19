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

- `main.py`：创建应用、挂载模块路由（无建表逻辑）
- `app/core/security.py`：密码哈希、令牌、当前用户依赖
- `app/modules/dept/`：第 5 章的单位模块（内存版，六文件齐备，保持不变）
- `app/modules/user/`：本章的用户模块（内存版：model、schema、crud、service、controller）

用户数据放在 `app/modules/user/model.py` 的 `TABLE` 列表里，重启即失。第 8 章数据模块才引入数据库，届时只改 `model.py` 与 `crud.py`，认证逻辑不动。

## 配置

复制 `.env.example` 为 `.env`，按本机情况填写；`.env` 不纳入 Git。
`SECRET_KEY` 是令牌签名密钥，正式部署必须替换示例值。
