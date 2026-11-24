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
TEST_DB_DIR = tempfile.mkdtemp(prefix="duty101-test-")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(TEST_DB_DIR) / "duty.db")

from app.core.database import SessionLocal, engine  # noqa: E402
from app.core.security import TOKEN_STORE  # noqa: E402
from app.modules.department.model import Department  # noqa: E402
from app.modules.duty_record.model import DutyRecord  # noqa: E402
from app.modules.personnel.model import Personnel  # noqa: E402
from app.modules.user import service as user_service  # noqa: E402
from app.modules.user.model import User  # noqa: E402
from app.modules.workstation.model import Workstation  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_tables():
    """每个用例从空库开始，并重建 admin/admin123，避免用例之间互相污染。"""
    TOKEN_STORE.clear()
    db = SessionLocal()
    try:
        db.query(DutyRecord).delete()
        db.query(Workstation).delete()
        db.query(Personnel).delete()
        db.query(Department).delete()
        db.query(User).delete()
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


def create_workstation(
    headers,
    workstation_id="W001",
    name="一号哨位",
    dept_code="D001",
    is_active=1,
):
    return client.post(
        "/workstations",
        json={
            "workstation_id": workstation_id,
            "name": name,
            "dept_code": dept_code,
            "is_active": is_active,
        },
        headers=headers,
    )


def create_record(
    headers,
    personnel_certificate_number="P001",
    workstation_id="W001",
    start_time="2026-03-02T08:00:00",
    end_time="2026-03-02T12:00:00",
    status="normal",
):
    return client.post(
        "/duty-records",
        json={
            "personnel_certificate_number": personnel_certificate_number,
            "workstation_id": workstation_id,
            "start_time": start_time,
            "end_time": end_time,
            "status": status,
        },
        headers=headers,
    )


def prepare_person_and_workstation(admin, dept_code="D001"):
    """建好一条记录所需的最小参照数据。"""
    assert create_department(admin, dept_code, "一中队").status_code == 201
    assert create_personnel(admin, "P001", "张伟", dept_code).status_code == 201
    assert create_workstation(admin, "W001", "一号哨位", dept_code).status_code == 201


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ---------- 哨位模块：CRUD、分页、字段与权限 ----------


def test_workstation_crud_public_read():
    admin = admin_headers()
    assert create_department(admin).status_code == 201

    created = create_workstation(admin, "W001", "一号哨位", "D001", 1)
    assert created.status_code == 201
    assert created.json() == {
        "workstation_id": "W001",
        "name": "一号哨位",
        "dept_code": "D001",
        "is_active": 1,
    }

    listed = client.get("/workstations")
    detail = client.get("/workstations/W001")

    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["workstation_id"] == "W001"
    assert detail.status_code == 200
    assert detail.json()["name"] == "一号哨位"

    updated = client.put(
        "/workstations/W001",
        json={
            "workstation_id": "W001",
            "name": "一号哨位（改）",
            "dept_code": "D001",
            "is_active": 0,
        },
        headers=admin,
    )
    assert updated.status_code == 200
    assert updated.json()["is_active"] == 0

    assert client.delete("/workstations/W001", headers=admin).status_code == 204
    assert client.get("/workstations/W001").status_code == 404
    assert client.delete("/workstations/W001", headers=admin).status_code == 404


def test_workstation_duplicate_and_unknown_department():
    admin = admin_headers()
    assert create_department(admin).status_code == 201
    assert create_workstation(admin).status_code == 201

    duplicate = create_workstation(admin)
    missing_dept = create_workstation(admin, "W002", "二号哨位", "D99")

    assert duplicate.status_code == 400
    assert duplicate.json() == {"detail": "哨位编号已存在"}
    assert missing_dept.status_code == 400
    assert missing_dept.json() == {"detail": "所属单位不存在"}


@pytest.mark.parametrize("is_active", [2, -1])
def test_workstation_invalid_is_active_returns_422(is_active):
    admin = admin_headers()
    assert create_department(admin).status_code == 201

    response = create_workstation(admin, is_active=is_active)

    assert response.status_code == 422


def test_workstation_list_pagination_and_filter():
    admin = admin_headers()
    assert create_department(admin, "D001", "一中队").status_code == 201
    assert create_department(admin, "D002", "二中队").status_code == 201
    for wid, dept in [("W001", "D001"), ("W002", "D001"), ("W03", "D002")]:
        assert create_workstation(admin, wid, wid, dept).status_code == 201

    first_page = client.get("/workstations", params={"page": 1, "page_size": 2})
    second_page = client.get("/workstations", params={"page": 2, "page_size": 2})
    filtered = client.get("/workstations", params={"dept_code": "D001"})

    assert [i["workstation_id"] for i in first_page.json()["items"]] == ["W001", "W002"]
    assert first_page.json()["total"] == 3
    assert [i["workstation_id"] for i in second_page.json()["items"]] == ["W03"]
    assert filtered.json()["total"] == 2
    assert client.get("/workstations", params={"page": 0}).status_code == 422


def test_workstation_write_requires_admin():
    admin = admin_headers()
    normal = normal_headers()
    assert create_department(admin).status_code == 201
    body = {
        "workstation_id": "W001",
        "name": "一号哨位",
        "dept_code": "D001",
        "is_active": 1,
    }

    assert client.post("/workstations", json=body).status_code == 401
    assert client.post("/workstations", json=body, headers=normal).status_code == 403
    assert create_workstation(admin).status_code == 201

    assert (
        client.put("/workstations/W001", json=body).status_code == 401
    )
    assert (
        client.put("/workstations/W001", json=body, headers=normal).status_code == 403
    )
    assert (
        client.delete("/workstations/W001", headers=normal).status_code == 403
    )
    assert client.get("/workstations").status_code == 200
    assert client.get("/workstations/W001").status_code == 200


# ---------- 执勤记录：新增、查询、删除 ----------


def test_duty_record_create_read_list_and_delete():
    admin = admin_headers()
    prepare_person_and_workstation(admin)

    created = create_record(admin)
    assert created.status_code == 201
    body = created.json()
    assert set(body) == {
        "id",
        "personnel_certificate_number",
        "workstation_id",
        "start_time",
        "end_time",
        "status",
    }
    assert body["personnel_certificate_number"] == "P001"
    assert body["workstation_id"] == "W001"
    assert body["start_time"].startswith("2026-03-02T08:00:00")
    assert body["end_time"].startswith("2026-03-02T12:00:00")
    assert body["status"] == "normal"

    record_id = body["id"]
    detail = client.get(f"/duty-records/{record_id}")
    listed = client.get("/duty-records")
    by_person = client.get(
        "/duty-records", params={"personnel_certificate_number": "P001"}
    )
    by_workstation = client.get("/duty-records", params={"workstation_id": "W001"})
    by_other = client.get(
        "/duty-records", params={"personnel_certificate_number": "P99"}
    )

    assert detail.status_code == 200
    assert detail.json()["id"] == record_id
    assert listed.json()["total"] == 1
    assert by_person.json()["total"] == 1
    assert by_workstation.json()["total"] == 1
    assert by_other.json() == {"items": [], "total": 0}

    assert client.delete(f"/duty-records/{record_id}", headers=admin).status_code == 204
    assert client.get(f"/duty-records/{record_id}").status_code == 404
    assert client.delete(f"/duty-records/{record_id}", headers=admin).status_code == 404


def test_duty_record_list_pagination_order_and_validation():
    admin = admin_headers()
    prepare_person_and_workstation(admin)
    assert create_record(admin, start_time="2026-03-02T08:00:00", end_time="2026-03-02T09:00:00").status_code == 201
    assert create_record(admin, start_time="2026-03-02T09:00:00", end_time="2026-03-02T10:00:00").status_code == 201
    assert create_record(admin, start_time="2026-03-02T10:00:00", end_time="2026-03-02T11:00:00").status_code == 201

    first_page = client.get("/duty-records", params={"page": 1, "page_size": 2})
    second_page = client.get("/duty-records", params={"page": 2, "page_size": 2})

    assert [i["id"] for i in first_page.json()["items"]] == [1, 2]
    assert first_page.json()["total"] == 3
    assert [i["id"] for i in second_page.json()["items"]] == [3]
    assert client.get("/duty-records", params={"page": 0}).status_code == 422
    assert client.get("/duty-records", params={"page_size": 101}).status_code == 422


# ---------- 规则一：开始时间必须早于结束时间 ----------


@pytest.mark.parametrize(
    "start_time,end_time",
    [
        ("2026-03-02T12:00:00", "2026-03-02T12:00:00"),
        ("2026-03-02T13:00:00", "2026-03-02T12:00:00"),
    ],
)
def test_rule_time_order_returns_400(start_time, end_time):
    admin = admin_headers()
    prepare_person_and_workstation(admin)

    response = create_record(admin, start_time=start_time, end_time=end_time)

    assert response.status_code == 400
    assert response.json() == {"detail": "开始时间必须早于结束时间"}


# ---------- 规则二：人员与哨位必须存在 ----------


def test_rule_unknown_personnel_returns_400():
    admin = admin_headers()
    prepare_person_and_workstation(admin)

    response = create_record(admin, personnel_certificate_number="P99")

    assert response.status_code == 400
    assert response.json() == {"detail": "人员不存在"}


def test_rule_unknown_workstation_returns_400():
    admin = admin_headers()
    prepare_person_and_workstation(admin)

    response = create_record(admin, workstation_id="W99")

    assert response.status_code == 400
    assert response.json() == {"detail": "哨位不存在"}


# ---------- 规则三：同一哨位时间不能重叠（含边界） ----------


@pytest.mark.parametrize(
    "start_time,end_time,expected_status,expected_detail",
    [
        # 被已有区间包含
        ("2026-03-02T10:00:00", "2026-03-02T11:00:00", 400, "该哨位在该时段已有执勤安排"),
        # 部分重叠
        ("2026-03-02T11:00:00", "2026-03-02T13:00:00", 400, "该哨位在该时段已有执勤安排"),
        # 完全相同
        ("2026-03-02T08:00:00", "2026-03-02T12:00:00", 400, "该哨位在该时段已有执勤安排"),
        # 首尾相接：不算冲突
        ("2026-03-02T12:00:00", "2026-03-02T14:00:00", 201, None),
        # 完全在之后
        ("2026-03-02T13:00:00", "2026-03-02T15:00:00", 201, None),
    ],
)
def test_rule_overlap_boundaries(start_time, end_time, expected_status, expected_detail):
    admin = admin_headers()
    prepare_person_and_workstation(admin)
    assert create_record(admin).status_code == 201  # 已有 08:00–12:00

    response = create_record(admin, start_time=start_time, end_time=end_time)

    assert response.status_code == expected_status
    if expected_detail is not None:
        assert response.json() == {"detail": expected_detail}


def test_rule_overlap_is_scoped_to_same_workstation():
    admin = admin_headers()
    prepare_person_and_workstation(admin)
    assert create_workstation(admin, "W002", "二号哨位", "D001").status_code == 201
    assert create_record(admin).status_code == 201

    other_workstation = create_record(admin, workstation_id="W002")

    assert other_workstation.status_code == 201


# ---------- 校验顺序与事务边界 ----------


def test_validation_order_time_before_personnel():
    admin = admin_headers()
    prepare_person_and_workstation(admin)

    response = create_record(
        admin,
        personnel_certificate_number="P99",
        start_time="2026-03-02T13:00:00",
        end_time="2026-03-02T12:00:00",
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "开始时间必须早于结束时间"}


def test_validation_order_personnel_before_workstation():
    admin = admin_headers()
    prepare_person_and_workstation(admin)

    response = create_record(admin, personnel_certificate_number="P99", workstation_id="W99")

    assert response.status_code == 400
    assert response.json() == {"detail": "人员不存在"}


def test_failed_create_leaves_no_row():
    admin = admin_headers()
    prepare_person_and_workstation(admin)
    before = client.get("/duty-records").json()["total"]

    failed = create_record(
        admin, start_time="2026-03-02T13:00:00", end_time="2026-03-02T12:00:00"
    )
    after = client.get("/duty-records").json()["total"]

    assert failed.status_code == 400
    assert before == 0
    assert after == 0


# ---------- 权限矩阵 ----------


def test_duty_record_write_requires_admin():
    admin = admin_headers()
    normal = normal_headers()
    prepare_person_and_workstation(admin)
    body = {
        "personnel_certificate_number": "P001",
        "workstation_id": "W001",
        "start_time": "2026-03-02T08:00:00",
        "end_time": "2026-03-02T12:00:00",
        "status": "normal",
    }

    assert client.post("/duty-records", json=body).status_code == 401
    assert client.post("/duty-records", json=body, headers=normal).status_code == 403

    created = create_record(admin)
    assert created.status_code == 201
    record_id = created.json()["id"]

    assert client.delete(f"/duty-records/{record_id}", headers=normal).status_code == 403
    assert client.get("/duty-records").status_code == 200
    assert client.get(f"/duty-records/{record_id}").status_code == 200
    assert client.delete(f"/duty-records/{record_id}", headers=admin).status_code == 204


# ---------- 9-1 / 8-1 / 7-1 回归 ----------


def test_users_permission_matrix_regression():
    anonymous = client.get("/users")
    normal = normal_headers()
    forbidden = client.get("/users", headers=normal)
    admin = client.get("/users", headers=admin_headers())

    assert anonymous.status_code == 401
    assert forbidden.status_code == 403
    assert admin.status_code == 200
    assert set(admin.json()) == {"items", "total"}
    assert "password_hash" not in admin.text


def test_department_write_requires_admin_regression():
    normal = normal_headers()
    admin = admin_headers()
    body = {"dept_code": "D001", "full_name": "一中队", "address": "一号营区"}

    assert client.post("/departments", json=body).status_code == 401
    assert client.post("/departments", json=body, headers=normal).status_code == 403
    assert create_department(admin).status_code == 201
    assert client.put("/departments/D001", json=body, headers=normal).status_code == 403
    assert client.delete("/departments/D001", headers=admin).status_code == 204


def test_register_login_me_regression():
    registered = register_user()
    assert registered.status_code == 201
    assert set(registered.json()) == {"id", "username", "role", "is_active"}
    assert "password_hash" not in registered.text

    assert register_user().status_code == 400
    assert register_user("bob", "12345").status_code == 422

    logged_in = login_user()
    assert logged_in.status_code == 200
    assert set(logged_in.json()) == {"access_token", "token_type", "user"}
    assert client.get("/users/me").status_code == 401

    me = client.get(
        "/users/me", headers=auth(logged_in.json()["access_token"])
    )
    assert me.status_code == 200
    assert me.json() == {"id": registered.json()["id"], "role": "normal"}
