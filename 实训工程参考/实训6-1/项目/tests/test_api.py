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
TEST_DB_DIR = tempfile.mkdtemp(prefix="duty61-test-")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(TEST_DB_DIR) / "duty.db")

from app.core.database import SessionLocal, engine  # noqa: E402
from app.modules.department.model import Department  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_departments():
    db = SessionLocal()
    try:
        db.query(Department).delete()
        db.commit()
    finally:
        db.close()
    yield


@pytest.fixture(scope="session", autouse=True)
def cleanup_temp_database():
    yield
    engine.dispose()
    shutil.rmtree(TEST_DB_DIR, ignore_errors=True)


def create_department(dept_code="D01", full_name="一中队", address="一号楼"):
    return client.post(
        "/departments",
        json={"dept_code": dept_code, "full_name": full_name, "address": address},
    )


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_list_departments_empty():
    response = client.get("/departments")

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0}


def test_create_and_get_department():
    created = create_department()

    assert created.status_code == 201
    assert created.json() == {
        "dept_code": "D01",
        "full_name": "一中队",
        "address": "一号楼",
    }

    response = client.get("/departments/D01")
    assert response.status_code == 200
    assert response.json() == created.json()


def test_missing_department_returns_404():
    assert client.get("/departments/D404").status_code == 404
    assert (
        client.put(
            "/departments/D404",
            json={"dept_code": "D404", "full_name": "不存在"},
        ).status_code
        == 404
    )
    assert client.delete("/departments/D404").status_code == 404


def test_duplicate_department_returns_400():
    create_department()

    response = create_department()

    assert response.status_code == 400
    assert response.json() == {"detail": "单位编码已存在"}


def test_update_department():
    create_department()

    response = client.put(
        "/departments/D01",
        json={"dept_code": "D01", "full_name": "第一中队", "address": "二号楼"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "dept_code": "D01",
        "full_name": "第一中队",
        "address": "二号楼",
    }


def test_delete_returns_204_without_body_and_second_delete_404():
    create_department()

    response = client.delete("/departments/D01")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/departments/D01").status_code == 404
    assert client.delete("/departments/D01").status_code == 404


def test_invalid_payload_returns_422():
    missing_name = client.post("/departments", json={"dept_code": "D01"})
    empty_code = create_department(dept_code="")
    too_long_name = create_department(dept_code="D02", full_name="单" * 101)
    too_long_address = create_department(
        dept_code="D03", full_name="三中队", address="地" * 501
    )

    assert missing_name.status_code == 422
    assert empty_code.status_code == 422
    assert too_long_name.status_code == 422
    assert too_long_address.status_code == 422


def test_pagination_returns_requested_slice_and_total():
    for index in range(1, 4):
        response = create_department(
            dept_code=f"D{index:02d}", full_name=f"第{index}中队"
        )
        assert response.status_code == 201

    first_page = client.get("/departments", params={"page": 1, "page_size": 2})
    second_page = client.get("/departments", params={"page": 2, "page_size": 2})
    third_page = client.get("/departments", params={"page": 3, "page_size": 2})
    default_page = client.get("/departments")

    assert first_page.status_code == 200
    assert first_page.json()["total"] == 3
    assert len(first_page.json()["items"]) == 2
    assert second_page.json()["total"] == 3
    assert len(second_page.json()["items"]) == 1
    assert {
        item["dept_code"] for item in first_page.json()["items"]
    } | {
        item["dept_code"] for item in second_page.json()["items"]
    } == {"D01", "D02", "D03"}
    assert third_page.json() == {"items": [], "total": 3}
    assert len(default_page.json()["items"]) == 3
    assert default_page.json()["total"] == 3


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page_size": 0},
        {"page_size": 101},
        {"page": "not-an-integer"},
    ],
)
def test_invalid_pagination_returns_422(params):
    response = client.get("/departments", params=params)

    assert response.status_code == 422
