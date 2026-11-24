import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from main import DEPARTMENTS, app


@pytest.fixture
def client():
    DEPARTMENTS.clear()
    DEPARTMENTS.update(
        {
            "D001": {
                "dept_code": "D001",
                "full_name": "一中队",
                "address": "一号营区",
            }
        }
    )
    with TestClient(app) as test_client:
        yield test_client


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_departments_returns_items_and_total(client):
    response = client.get("/departments")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"] == [
        {"dept_code": "D001", "full_name": "一中队", "address": "一号营区"}
    ]


def test_get_department_returns_200(client):
    response = client.get("/departments/D001")

    assert response.status_code == 200
    assert response.json() == {
        "dept_code": "D001",
        "full_name": "一中队",
        "address": "一号营区",
    }


def test_get_missing_department_returns_404(client):
    response = client.get("/departments/D404")

    assert response.status_code == 404
    assert response.json() == {"detail": "单位不存在"}


def test_create_department_returns_201(client):
    response = client.post(
        "/departments",
        json={"dept_code": "D002", "full_name": "二中队", "address": "二号营区"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "dept_code": "D002",
        "full_name": "二中队",
        "address": "二号营区",
    }


def test_create_duplicate_department_returns_400(client):
    response = client.post(
        "/departments",
        json={"dept_code": "D001", "full_name": "重复单位"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "单位编码已存在"}


def test_create_department_without_required_field_returns_400(client):
    response = client.post("/departments", json={"dept_code": "D002"})

    assert response.status_code == 400
    assert response.json() == {"detail": "缺少必填字段"}


def test_update_department_returns_200(client):
    response = client.put("/departments/D001", json={"full_name": "一中队（改）"})

    assert response.status_code == 200
    assert response.json() == {
        "dept_code": "D001",
        "full_name": "一中队（改）",
        "address": "一号营区",
    }


def test_update_missing_department_returns_404(client):
    response = client.put("/departments/D404", json={"full_name": "不存在"})

    assert response.status_code == 404
    assert response.json() == {"detail": "单位不存在"}


def test_delete_department_returns_204_without_body(client):
    response = client.delete("/departments/D001")

    assert response.status_code == 204
    assert response.content == b""
    assert "D001" not in DEPARTMENTS


def test_delete_department_twice_returns_404(client):
    first_response = client.delete("/departments/D001")
    second_response = client.delete("/departments/D001")

    assert first_response.status_code == 204
    assert second_response.status_code == 404
    assert second_response.json() == {"detail": "单位不存在"}
