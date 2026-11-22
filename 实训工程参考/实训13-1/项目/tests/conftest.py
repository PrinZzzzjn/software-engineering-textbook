"""测试夹具：client、admin_headers 与管理员种子。

对应教材 12.3 的代码 12-3-1。唯一的教师版增强：在导入 main 之前把
DATABASE_URL 指向系统临时目录，测试不碰开发库，也不在仓库生成 duty.db
（对应教材 12.4「独立测试库」的课后扩展）。
"""

import os
import shutil
import tempfile
import uuid
from pathlib import Path

_TEST_DB_DIR = tempfile.mkdtemp(prefix="duty121-test-")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(_TEST_DB_DIR) / "duty.db")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import SessionLocal, engine  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.modules.user.model import User  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def seed_admin():
    """在测试进程里确保管理员账号存在，供各登录用例共用。"""
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == "admin").first() is None:
            db.add(
                User(
                    username="admin",
                    password_hash=get_password_hash("admin123"),
                    role="admin",
                    is_active=1,
                )
            )
            db.commit()
    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_headers(client):
    resp = client.post(
        "/users/login", json={"username": "admin", "password": "admin123"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def normal_headers(client):
    """13-1 新增：注册并登录一个普通用户，用于 401 与 403 的对照。"""
    username = f"normal_{uuid.uuid4().hex[:8]}"
    client.post("/users", json={"username": username, "password": "normal123"})
    resp = client.post(
        "/users/login", json={"username": username, "password": "normal123"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def db_session():
    """13-1 新增：直接调用 service 层验证事务边界时使用的会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_database():
    """整轮测试结束后释放连接并删除临时库（教师版增强）。"""
    yield
    engine.dispose()
    shutil.rmtree(_TEST_DB_DIR, ignore_errors=True)
