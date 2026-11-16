# -*- coding: utf-8 -*-
"""第 6、7 章示例代码回归：按两章印刷的代码原样运行。

用法：python docs/_验证/run_user_module_test.py
"""
import os
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE / "用户模块"
DB = PROJECT / "verify_user.db"
ENV = PROJECT / ".env"
if DB.exists():
    DB.unlink()
ENV.write_text('SECRET_KEY="test-secret"\n', encoding="utf-8")
os.chdir(PROJECT)

sys.path.insert(0, str(PROJECT))

from fastapi.testclient import TestClient  # noqa: E402
import main  # noqa: E402
from app.core import security  # noqa: E402
from app.scripts.create_admin import create_admin  # noqa: E402

client = TestClient(main.app)
results = []


def check(name, resp, status, predicate=None):
    ok = resp.status_code == status
    if ok and predicate is not None:
        ok = predicate(resp)
    results.append((name, ok, resp.status_code, resp.text[:160]))
    return resp


def check_bool(name, value, detail=""):
    results.append((name, bool(value), "-", detail[:160]))


def auth(token):
    return {"Authorization": f"Bearer {token}"}


check_bool(".env 中的 SECRET_KEY 生效", security.SECRET_KEY == "test-secret",
           f"读到 {security.SECRET_KEY}")

# 注册
r = check("注册成功（无尾斜杠，不跟随重定向）",
          client.post("/api/v1/users", json={
              "username": "alice", "password": "secret123"},
              follow_redirects=False), 201,
          lambda x: "password_hash" not in x.json())
alice_id = r.json()["id"] if r.status_code == 201 else 0

check("重复用户名", client.post("/api/v1/users", json={
    "username": "alice", "password": "secret123"}), 400)
check("输入过短", client.post("/api/v1/users", json={
    "username": "ab", "password": "123"}), 422)

# 登录
r = check("登录成功", client.post("/api/v1/users/login", json={
    "username": "alice", "password": "secret123"}), 200,
    lambda x: "access_token" in x.json())
alice_token = r.json().get("access_token", "") if r.status_code == 200 else ""
check("密码错误", client.post("/api/v1/users/login", json={
    "username": "alice", "password": "wrong"}), 401)

# 受保护接口
check("未带令牌访问 /me", client.get("/api/v1/users/me"), 401)
check("坏令牌访问 /me", client.get("/api/v1/users/me",
      headers=auth("not-a-token")), 401)
check("带令牌访问 /me", client.get("/api/v1/users/me", headers=auth(alice_token)), 200,
      lambda x: isinstance(x.json()["id"], int) and x.json()["role"] == "normal")

# 管理员：先占用同名普通账号，再由脚本提升
check("先注册同名普通账号", client.post("/api/v1/users", json={
    "username": "admin", "password": "normalpass"}), 201)
create_admin()
r = check("同名普通账号可提升为管理员", client.post("/api/v1/users/login", json={
    "username": "admin", "password": "admin123"}), 200,
    lambda x: "access_token" in x.json())
admin_token = r.json().get("access_token", "") if r.status_code == 200 else ""
me = client.get("/api/v1/users/me", headers=auth(admin_token))
admin_id = me.json().get("id", 0) if me.status_code == 200 else 0
check("提升后角色为 admin", client.get("/api/v1/users/me", headers=auth(admin_token)), 200,
      lambda x: x.json()["role"] == "admin")

check("未登录访问列表", client.get("/api/v1/users", follow_redirects=False), 401)
check("普通用户访问列表", client.get("/api/v1/users",
      headers=auth(alice_token), follow_redirects=False), 403)
check("管理员访问列表", client.get("/api/v1/users",
      headers=auth(admin_token), follow_redirects=False), 200,
      lambda x: x.json()["count"] >= 2)

# 修改与业务规则
check("非法角色", client.put(f"/api/v1/users/{alice_id}",
      json={"role": "superuser"}, headers=auth(admin_token)), 422)
check("用户不存在", client.put("/api/v1/users/999999",
      json={"is_active": 0}, headers=auth(admin_token)), 404)
check("禁用自己", client.put(f"/api/v1/users/{admin_id}",
      json={"is_active": 0}, headers=auth(admin_token)), 400)
check("禁用普通用户", client.put(f"/api/v1/users/{alice_id}",
      json={"is_active": 0}, headers=auth(admin_token)), 200)
check("禁用后登录", client.post("/api/v1/users/login", json={
    "username": "alice", "password": "secret123"}), 401)
check("重新启用", client.put(f"/api/v1/users/{alice_id}",
      json={"is_active": 1}, headers=auth(admin_token)), 200)

# /docs 的 Authorize 使用 HTTPBearer，可直接粘贴登录得到的令牌
scheme = client.get("/openapi.json").json()["components"]["securitySchemes"]
check_bool("OpenAPI 安全方案为 HTTPBearer", "HTTPBearer" in scheme, str(scheme))

failed = [x for x in results if not x[1]]
for name, ok, status, body in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}  -> {status}  {body}")
print(f"\n{len(results) - len(failed)}/{len(results)} PASS")
sys.exit(1 if failed else 0)
