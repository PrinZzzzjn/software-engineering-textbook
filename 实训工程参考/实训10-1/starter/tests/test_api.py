import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# 关键：在导入 main 之前把数据库指向临时文件，测试不会在仓库目录生成 duty.db
TEST_DB_DIR = tempfile.mkdtemp(prefix="duty91-test-")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(TEST_DB_DIR) / "duty.db")

from app.core.database import SessionLocal, engine  # noqa: E402
from app.core.security import TOKEN_STORE  # noqa: E402
from app.modules.department.model import Department  # noqa: E402
from app.modules.personnel.model import Personnel  # noqa: E402
from app.modules.user import service as user_service  # noqa: E402
from app.modules.user.model import User  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_tables():
    """每个用例从空库开始，并重建 admin/admin123，避免用例之间互相污染。"""
    TOKEN_STORE.clear()
    db = SessionLocal()
    try:
        db.query(User).delete()
        db.query(Personnel).delete()
        db.query(Department).delete()
        db.commit()
        user_service.create_admin(db)
    finally:
        db.close()
    yield


@pytest.fixture(scope="session", autouse=True)
def cleanup_temp_database():
    yield
    engine.dispose()
    shutil.rmtree(TEST_DB_DIR, ignore_errors=True)


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def register_user(username="alice", password="secret123"):
    return client.post("/users", json={"username": username, "password": password})


def login_user(username="alice", password="secret123"):
    return client.post(
        "/users/login", json={"username": username, "password": password}
    )


def admin_headers():
    response = login_user("admin", "admin123")
    assert response.status_code == 200
    return auth(response.json()["access_token"])


def normal_headers(username="alice", password="secret123"):
    assert register_user(username, password).status_code == 201
    response = login_user(username, password)
    assert response.status_code == 200
    return auth(response.json()["access_token"])


def create_department(headers, dept_code="D001", full_name="一中队", address="一号营区"):
    return client.post(
        "/departments",
        json={"dept_code": dept_code, "full_name": full_name, "address": address},
        headers=headers,
    )


def create_personnel(
    headers,
    certificate_number="P001",
    name="张伟",
    dept_code="D001",
    rank="一级值班员",
):
    return client.post(
        "/personnel",
        json={
            "certificate_number": certificate_number,
            "name": name,
            "dept_code": dept_code,
            "rank": rank,
        },
        headers=headers,
    )


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ---------- 管理员依赖：401 / 403 / 200 ----------


def test_user_list_anonymous_401_normal_403_admin_200():
    anonymous = client.get("/users")

    assert anonymous.status_code == 401
    assert anonymous.json() == {"detail": "未提供令牌"}

    normal = normal_headers()
    forbidden = client.get("/users", headers=normal)

    assert forbidden.status_code == 403
    assert forbidden.json() == {"detail": "权限不足"}

    admin = client.get("/users", headers=admin_headers())

    assert admin.status_code == 200
    assert set(admin.json()) == {"items", "total"}
    assert "password_hash" not in admin.text


def test_user_list_invalid_token_returns_401():
    response = client.get("/users", headers=auth("not-registered"))

    assert response.status_code == 401
    assert response.json() == {"detail": "令牌无效"}


# ---------- 用户列表：分页、排序、字段过滤 ----------


def test_user_list_pagination_order_and_public_fields():
    admin = admin_headers()
    alice = register_user("alice").json()
    bob = register_user("bob").json()
    carol = register_user("carol").json()

    first_page = client.get("/users", params={"page": 1, "page_size": 2}, headers=admin)
    second_page = client.get("/users", params={"page": 2, "page_size": 2}, headers=admin)
    third_page = client.get("/users", params={"page": 3, "page_size": 2}, headers=admin)
    default_page = client.get("/users", headers=admin)

    assert first_page.status_code == 200
    assert [item["username"] for item in first_page.json()["items"]] == [
        "admin",
        "alice",
    ]
    assert first_page.json()["total"] == 4
    assert [item["username"] for item in second_page.json()["items"]] == [
        "bob",
        "carol",
    ]
    assert second_page.json()["total"] == 4
    assert third_page.json() == {"items": [], "total": 4}
    assert default_page.json()["total"] == 4
    assert len(default_page.json()["items"]) == 4

    for item in default_page.json()["items"]:
        assert set(item) == {"id", "username", "role", "is_active"}
    assert {"id": alice["id"], "username": "alice", "role": "normal", "is_active": 1} in (
        default_page.json()["items"]
    )
    assert {"id": bob["id"], "username": "bob", "role": "normal", "is_active": 1} in (
        default_page.json()["items"]
    )
    assert {"id": carol["id"], "username": "carol", "role": "normal", "is_active": 1} in (
        default_page.json()["items"]
    )
    assert "password_hash" not in default_page.text


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page_size": 0},
        {"page_size": 101},
        {"page": "not-an-integer"},
    ],
)
def test_user_list_invalid_pagination_returns_422(params):
    response = client.get("/users", params=params, headers=admin_headers())

    assert response.status_code == 422


# ---------- 修改用户：200 / 400 / 404 / 422 ----------


def test_update_user_role_and_status_200():
    admin = admin_headers()
    alice = register_user("alice").json()
    alice_token = login_user("alice").json()["access_token"]

    promoted = client.put(
        f"/users/{alice['id']}", json={"role": "admin"}, headers=admin
    )

    assert promoted.status_code == 200
    assert promoted.json() == {
        "id": alice["id"],
        "username": "alice",
        "role": "admin",
        "is_active": 1,
    }
    assert "password_hash" not in promoted.text

    # 角色在每次校验令牌时从用户表读取，改角色后旧令牌立即按新角色放行
    assert client.get("/users", headers=auth(alice_token)).status_code == 200

    disabled = client.put(
        f"/users/{alice['id']}", json={"is_active": 0}, headers=admin
    )

    assert disabled.status_code == 200
    assert disabled.json()["is_active"] == 0

    blocked_login = login_user("alice")
    assert blocked_login.status_code == 401
    assert blocked_login.json() == {"detail": "账号已禁用"}

    enabled = client.put(f"/users/{alice['id']}", json={"is_active": 1}, headers=admin)

    assert enabled.status_code == 200
    assert enabled.json()["is_active"] == 1
    assert login_user("alice").status_code == 200


def test_update_user_not_found_returns_404():
    response = client.put(
        "/users/99999", json={"role": "normal"}, headers=admin_headers()
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "用户不存在"}


def test_update_user_cannot_disable_self_returns_400():
    admin = admin_headers()
    me = client.get("/users/me", headers=admin).json()

    response = client.put(
        f"/users/{me['id']}", json={"is_active": 0}, headers=admin
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "不能禁用自己"}


@pytest.mark.parametrize(
    "payload",
    [
        {"role": "superuser"},
        {"is_active": 2},
        {"is_active": -1},
    ],
)
def test_update_user_invalid_values_returns_422(payload):
    admin = admin_headers()
    alice = register_user("alice").json()

    response = client.put(f"/users/{alice['id']}", json=payload, headers=admin)

    assert response.status_code == 422


def test_update_user_anonymous_401_and_normal_403():
    alice = register_user("alice").json()
    bob = register_user("bob").json()
    bob_token = login_user("bob").json()["access_token"]

    anonymous = client.put(f"/users/{alice['id']}", json={"role": "admin"})
    normal = client.put(
        f"/users/{alice['id']}",
        json={"role": "admin"},
        headers=auth(bob_token),
    )

    assert anonymous.status_code == 401
    assert normal.status_code == 403
    assert client.get("/users/me", headers=auth(bob_token)).status_code == 200
    assert bob["role"] == "normal"


# ---------- 权限回收：department 写操作 ----------


def test_department_write_requires_admin():
    anonymous = {}
    normal = normal_headers()
    admin = admin_headers()

    body = {"dept_code": "D001", "full_name": "一中队", "address": "一号营区"}

    assert client.post("/departments", json=body, headers=anonymous).status_code == 401
    assert client.post("/departments", json=body, headers=normal).status_code == 403

    created = create_department(admin)
    assert created.status_code == 201

    assert (
        client.put(
            "/departments/D001",
            json={"dept_code": "D001", "full_name": "一中队（改）"},
            headers=anonymous,
        ).status_code
        == 401
    )
    assert (
        client.put(
            "/departments/D001",
            json={"dept_code": "D001", "full_name": "一中队（改）"},
            headers=normal,
        ).status_code
        == 403
    )
    updated = client.put(
        "/departments/D001",
        json={"dept_code": "D001", "full_name": "一中队（改）"},
        headers=admin,
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "一中队（改）"

    assert client.delete("/departments/D001", headers=anonymous).status_code == 401
    assert client.delete("/departments/D001", headers=normal).status_code == 403
    assert client.delete("/departments/D001", headers=admin).status_code == 204


def test_department_read_remains_public():
    admin = admin_headers()
    assert create_department(admin).status_code == 201

    listed = client.get("/departments")
    detail = client.get("/departments/D001")

    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert detail.status_code == 200
    assert detail.json()["dept_code"] == "D001"


# ---------- 权限回收：personnel 写操作 ----------


def test_personnel_write_requires_admin():
    admin = admin_headers()
    normal = normal_headers()
    assert create_department(admin).status_code == 201

    body = {
        "certificate_number": "P001",
        "name": "张伟",
        "dept_code": "D001",
        "rank": "一级值班员",
    }

    assert client.post("/personnel", json=body).status_code == 401
    assert client.post("/personnel", json=body, headers=normal).status_code == 403

    created = create_personnel(admin)
    assert created.status_code == 201

    update_body = {
        "certificate_number": "P001",
        "name": "张伟（改）",
        "dept_code": "D001",
        "rank": "副一级值班员",
    }
    assert client.put("/personnel/P001", json=update_body).status_code == 401
    assert (
        client.put("/personnel/P001", json=update_body, headers=normal).status_code
        == 403
    )
    updated = client.put("/personnel/P001", json=update_body, headers=admin)
    assert updated.status_code == 200
    assert updated.json()["name"] == "张伟（改）"

    assert client.delete("/personnel/P001").status_code == 401
    assert client.delete("/personnel/P001", headers=normal).status_code == 403
    assert client.delete("/personnel/P001", headers=admin).status_code == 204


def test_personnel_read_remains_public():
    admin = admin_headers()
    assert create_department(admin).status_code == 201
    assert create_personnel(admin).status_code == 201

    listed = client.get("/personnel")
    detail = client.get("/personnel/P001")

    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert detail.status_code == 200
    assert detail.json()["certificate_number"] == "P001"


# ---------- 8-1 注册 / 登录 / me 回归 ----------


def test_register_login_me_regression():
    registered = register_user()
    assert registered.status_code == 201
    assert set(registered.json()) == {"id", "username", "role", "is_active"}
    assert registered.json()["role"] == "normal"
    assert "password_hash" not in registered.text

    duplicate = register_user()
    assert duplicate.status_code == 400
    assert duplicate.json() == {"detail": "用户名已存在"}

    assert register_user("bob", "12345").status_code == 422

    logged_in = login_user()
    assert logged_in.status_code == 200
    body = logged_in.json()
    assert set(body) == {"access_token", "token_type", "user"}
    assert body["token_type"] == "bearer"
    assert set(body["user"]) == {"id", "username", "role", "is_active"}
    assert "password_hash" not in logged_in.text

    assert login_user(password="wrong").status_code == 401
    assert client.get("/users/me").status_code == 401
    assert client.get("/users/me").json() == {"detail": "未提供令牌"}

    me = client.get(
        "/users/me", headers=auth(logged_in.json()["access_token"])
    )
    assert me.status_code == 200
    assert me.json() == {"id": registered.json()["id"], "role": "normal"}


def test_register_ignores_client_supplied_role():
    response = client.post(
        "/users",
        json={"username": "bob", "password": "secret123", "role": "admin"},
    )

    assert response.status_code == 201
    assert response.json()["role"] == "normal"


# ---------- 7-1 查询行为回归 ----------


def test_department_query_regression():
    admin = admin_headers()
    for code, name in [("D001", "一中队"), ("D002", "二中队"), ("D03", "三中队")]:
        assert create_department(admin, code, name).status_code == 201

    first_page = client.get("/departments", params={"page": 1, "page_size": 2})
    second_page = client.get("/departments", params={"page": 2, "page_size": 2})
    filtered = client.get("/departments", params={"full_name": "二中"})
    blank = client.get("/departments", params={"full_name": ""})

    assert first_page.status_code == 200
    assert [item["dept_code"] for item in first_page.json()["items"]] == [
        "D001",
        "D002",
    ]
    assert first_page.json()["total"] == 3
    assert [item["dept_code"] for item in second_page.json()["items"]] == ["D03"]
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["dept_code"] == "D002"
    assert blank.json()["total"] == 3
    assert client.get("/departments", params={"page": 0}).status_code == 422


def test_personnel_query_regression():
    admin = admin_headers()
    assert create_department(admin, "D001", "一中队").status_code == 201
    assert create_department(admin, "D002", "二中队").status_code == 201
    assert create_personnel(admin, "P001", "张伟", "D001").status_code == 201
    assert create_personnel(admin, "P002", "李四", "D001").status_code == 201
    assert create_personnel(admin, "P03", "张伟丰", "D002").status_code == 201

    name_hit = client.get("/personnel", params={"name": "张"})
    dept_hit = client.get("/personnel", params={"dept_code": "D001"})
    paged = client.get("/personnel", params={"page": 2, "page_size": 2})

    assert name_hit.status_code == 200
    assert [
        item["certificate_number"] for item in name_hit.json()["items"]
    ] == ["P001", "P03"]
    assert name_hit.json()["total"] == 2
    assert dept_hit.json()["total"] == 2
    assert [item["certificate_number"] for item in paged.json()["items"]] == ["P03"]
    assert paged.json()["total"] == 3
    assert client.get("/personnel", params={"page_size": 101}).status_code == 422
