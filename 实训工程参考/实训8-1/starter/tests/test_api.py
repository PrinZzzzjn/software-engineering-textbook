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
TEST_DB_DIR = tempfile.mkdtemp(prefix="duty71-test-")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(TEST_DB_DIR) / "duty.db")

from app.core.database import SessionLocal, engine  # noqa: E402
from app.modules.department.model import Department  # noqa: E402
from app.modules.personnel.model import Personnel  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_tables():
    db = SessionLocal()
    try:
        db.query(Personnel).delete()
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


def create_department(dept_code="D001", full_name="一中队", address="一号营区"):
    return client.post(
        "/departments",
        json={"dept_code": dept_code, "full_name": full_name, "address": address},
    )


def create_personnel(
    certificate_number="P001", name="张伟", dept_code="D001", rank="一级值班员"
):
    return client.post(
        "/personnel",
        json={
            "certificate_number": certificate_number,
            "name": name,
            "dept_code": dept_code,
            "rank": rank,
        },
    )


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ---------- department：分页、过滤、固定排序 ----------


def test_department_list_pagination_and_total():
    for index in range(1, 4):
        response = create_department(f"D{index:02d}", f"第{index}中队")
        assert response.status_code == 201

    first_page = client.get("/departments", params={"page": 1, "page_size": 2})
    second_page = client.get("/departments", params={"page": 2, "page_size": 2})
    third_page = client.get("/departments", params={"page": 3, "page_size": 2})
    default_page = client.get("/departments")

    assert first_page.status_code == 200
    assert [item["dept_code"] for item in first_page.json()["items"]] == [
        "D001",
        "D002",
    ]
    assert first_page.json()["total"] == 3
    assert [item["dept_code"] for item in second_page.json()["items"]] == ["D03"]
    assert second_page.json()["total"] == 3
    assert third_page.json() == {"items": [], "total": 3}
    assert len(default_page.json()["items"]) == 3
    assert default_page.json()["total"] == 3


def test_department_filter_full_name_hit_and_miss():
    create_department("D001", "一中队")
    create_department("D002", "二中队")
    create_department("D03", "三中队")

    hit = client.get("/departments", params={"full_name": "二中"})
    paged_hit = client.get(
        "/departments", params={"full_name": "中队", "page_size": 2}
    )
    miss = client.get("/departments", params={"full_name": "不存在"})
    blank = client.get("/departments", params={"full_name": ""})

    assert hit.status_code == 200
    assert [item["dept_code"] for item in hit.json()["items"]] == ["D002"]
    assert hit.json()["total"] == 1
    assert paged_hit.status_code == 200
    assert [item["dept_code"] for item in paged_hit.json()["items"]] == [
        "D001",
        "D002",
    ]
    assert paged_hit.json()["total"] == 3
    assert miss.status_code == 200
    assert miss.json() == {"items": [], "total": 0}
    assert blank.status_code == 200
    assert blank.json()["total"] == 3


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page_size": 0},
        {"page_size": 101},
        {"page": "not-an-integer"},
    ],
)
def test_department_invalid_pagination_returns_422(params):
    response = client.get("/departments", params=params)

    assert response.status_code == 422


def test_department_invalid_payload_returns_422():
    missing_name = client.post("/departments", json={"dept_code": "D001"})
    empty_code = create_department(dept_code="")
    too_long_name = create_department(dept_code="D002", full_name="单" * 101)
    too_long_address = create_department(
        dept_code="D03", full_name="三中队", address="地" * 501
    )

    assert missing_name.status_code == 422
    assert empty_code.status_code == 422
    assert too_long_name.status_code == 422
    assert too_long_address.status_code == 422


def test_department_detail_200_and_404():
    created = create_department()
    assert created.status_code == 201

    found = client.get("/departments/D001")
    assert found.status_code == 200
    assert found.json() == created.json()

    assert client.get("/departments/D404").status_code == 404
    assert (
        client.put(
            "/departments/D404",
            json={"dept_code": "D404", "full_name": "不存在"},
        ).status_code
        == 404
    )
    assert client.delete("/departments/D404").status_code == 404


def test_department_create_201_and_duplicate_400():
    created = create_department()

    assert created.status_code == 201
    assert created.json() == {
        "dept_code": "D001",
        "full_name": "一中队",
        "address": "一号营区",
    }

    duplicate = create_department()
    assert duplicate.status_code == 400
    assert duplicate.json() == {"detail": "单位编码已存在"}


def test_department_update_returns_200():
    create_department()

    response = client.put(
        "/departments/D001",
        json={"dept_code": "D001", "full_name": "第一中队", "address": "二号营区"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "dept_code": "D001",
        "full_name": "第一中队",
        "address": "二号营区",
    }


def test_department_delete_204_then_404():
    create_department()

    response = client.delete("/departments/D001")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/departments/D001").status_code == 404
    assert client.delete("/departments/D001").status_code == 404


# ---------- personnel：同一套分页与过滤写法 ----------


def test_personnel_list_pagination_and_total():
    create_department("D001", "一中队")
    create_department("D002", "二中队")
    assert create_personnel("P001", "张伟", "D001").status_code == 201
    assert create_personnel("P002", "李四", "D001").status_code == 201
    assert create_personnel("P03", "王五", "D002").status_code == 201

    first_page = client.get("/personnel", params={"page": 1, "page_size": 2})
    second_page = client.get("/personnel", params={"page": 2, "page_size": 2})
    third_page = client.get("/personnel", params={"page": 3, "page_size": 2})
    default_page = client.get("/personnel")

    assert first_page.status_code == 200
    assert [
        item["certificate_number"] for item in first_page.json()["items"]
    ] == ["P001", "P002"]
    assert first_page.json()["total"] == 3
    assert [
        item["certificate_number"] for item in second_page.json()["items"]
    ] == ["P03"]
    assert second_page.json()["total"] == 3
    assert third_page.json() == {"items": [], "total": 3}
    assert len(default_page.json()["items"]) == 3
    assert default_page.json()["total"] == 3


def test_personnel_filter_hit_and_miss():
    create_department("D001", "一中队")
    create_department("D002", "二中队")
    create_personnel("P001", "张伟", "D001")
    create_personnel("P002", "李四", "D001")
    create_personnel("P03", "张伟丰", "D002")

    name_hit = client.get("/personnel", params={"name": "张"})
    dept_hit = client.get("/personnel", params={"dept_code": "D001"})
    name_miss = client.get("/personnel", params={"name": "王"})
    dept_miss = client.get("/personnel", params={"dept_code": "D99"})
    blank = client.get("/personnel", params={"name": ""})

    assert name_hit.status_code == 200
    assert [
        item["certificate_number"] for item in name_hit.json()["items"]
    ] == ["P001", "P03"]
    assert name_hit.json()["total"] == 2
    assert dept_hit.status_code == 200
    assert [
        item["certificate_number"] for item in dept_hit.json()["items"]
    ] == ["P001", "P002"]
    assert dept_hit.json()["total"] == 2
    assert name_miss.status_code == 200
    assert name_miss.json() == {"items": [], "total": 0}
    assert dept_miss.status_code == 200
    assert dept_miss.json() == {"items": [], "total": 0}
    assert blank.status_code == 200
    assert blank.json()["total"] == 3


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page_size": 0},
        {"page_size": 101},
        {"page": "not-an-integer"},
    ],
)
def test_personnel_invalid_pagination_returns_422(params):
    response = client.get("/personnel", params=params)

    assert response.status_code == 422


def test_personnel_invalid_payload_returns_422():
    missing_name = client.post(
        "/personnel", json={"certificate_number": "P001", "dept_code": "D001"}
    )
    empty_number = create_personnel(certificate_number="")
    empty_dept = create_personnel(certificate_number="P002", dept_code="")
    too_long_rank = create_personnel(certificate_number="P03", rank="级" * 51)

    assert missing_name.status_code == 422
    assert empty_number.status_code == 422
    assert empty_dept.status_code == 422
    assert too_long_rank.status_code == 422


def test_personnel_detail_200_and_404():
    create_department("D001", "一中队")
    created = create_personnel()

    assert created.status_code == 201

    found = client.get("/personnel/P001")
    assert found.status_code == 200
    assert found.json() == created.json()

    assert client.get("/personnel/P404").status_code == 404
    assert (
        client.put(
            "/personnel/P404",
            json={
                "certificate_number": "P404",
                "name": "不存在",
                "dept_code": "D001",
            },
        ).status_code
        == 404
    )
    assert client.delete("/personnel/P404").status_code == 404


def test_personnel_create_201_duplicate_400_and_missing_department_400():
    create_department("D001", "一中队")

    created = create_personnel()

    assert created.status_code == 201
    assert created.json() == {
        "certificate_number": "P001",
        "name": "张伟",
        "dept_code": "D001",
        "rank": "一级值班员",
    }

    duplicate = create_personnel()
    assert duplicate.status_code == 400
    assert duplicate.json() == {"detail": "证件号已存在"}

    missing_department = create_personnel("P002", "李四", "D99")
    assert missing_department.status_code == 400
    assert missing_department.json() == {"detail": "所属单位不存在"}


def test_personnel_update_returns_200():
    create_department("D001", "一中队")
    create_personnel()

    response = client.put(
        "/personnel/P001",
        json={
            "certificate_number": "P001",
            "name": "张伟（改）",
            "dept_code": "D001",
            "rank": "副一级值班员",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "certificate_number": "P001",
        "name": "张伟（改）",
        "dept_code": "D001",
        "rank": "副一级值班员",
    }


def test_personnel_delete_204_then_404():
    create_department("D001", "一中队")
    create_personnel()

    response = client.delete("/personnel/P001")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/personnel/P001").status_code == 404
    assert client.delete("/personnel/P001").status_code == 404
