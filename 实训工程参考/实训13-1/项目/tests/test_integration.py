"""教材 13.4 的 12 步联调清单，逐步固化为接口用例。

每步对应联调记录表中的一行：请求 → 期望 → 实际。用例之间不共享数据，
每一步都自己准备前置资源，失败时能直接定位到断点。
"""

import random
import uuid
from datetime import date, timedelta


def _unique(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex[:6].upper()}"


def _future_day() -> date:
    # 与 12-1 的 1000~2000 天错开，避免两批测试落到同一年
    return date.today() + timedelta(days=random.randint(3000, 4000))


def _create_chain(client, admin_headers):
    """按真实顺序建单位 → 人员 → 哨位，返回三个唯一编号。"""
    dept_code = _unique("D")
    certificate = _unique("P")
    workstation_id = _unique("W")
    assert (
        client.post(
            "/departments",
            json={"dept_code": dept_code, "full_name": "联调单位"},
            headers=admin_headers,
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/personnel",
            json={
                "certificate_number": certificate,
                "name": "联调人员",
                "dept_code": dept_code,
            },
            headers=admin_headers,
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/workstations",
            json={
                "workstation_id": workstation_id,
                "name": "联调哨位",
                "dept_code": dept_code,
            },
            headers=admin_headers,
        ).status_code
        == 201
    )
    return dept_code, certificate, workstation_id


def test_step01_admin_login(client):
    resp = client.post(
        "/users/login", json={"username": "admin", "password": "admin123"}
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_step02_create_normal_user(client):
    username = f"normal_{uuid.uuid4().hex[:8]}"
    resp = client.post(
        "/users", json={"username": username, "password": "normal123"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == username
    assert body["role"] == "normal"
    assert "password_hash" not in body


def test_step03_normal_user_login(client):
    username = f"normal_{uuid.uuid4().hex[:8]}"
    assert (
        client.post(
            "/users", json={"username": username, "password": "normal123"}
        ).status_code
        == 201
    )
    resp = client.post(
        "/users/login", json={"username": username, "password": "normal123"}
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_step04_normal_user_cannot_list_users(client, normal_headers):
    assert client.get("/users", headers=normal_headers).status_code == 403


def test_step05_admin_create_department(client, admin_headers):
    dept_code = _unique("D")
    resp = client.post(
        "/departments",
        json={"dept_code": dept_code, "full_name": "联调单位"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["dept_code"] == dept_code


def test_step06_admin_create_personnel(client, admin_headers):
    dept_code = _unique("D")
    assert (
        client.post(
            "/departments",
            json={"dept_code": dept_code, "full_name": "联调单位"},
            headers=admin_headers,
        ).status_code
        == 201
    )
    certificate = _unique("P")
    resp = client.post(
        "/personnel",
        json={
            "certificate_number": certificate,
            "name": "联调人员",
            "dept_code": dept_code,
        },
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["dept_code"] == dept_code


def test_step07_admin_create_duty_record(client, admin_headers):
    _, certificate, workstation_id = _create_chain(client, admin_headers)
    day = _future_day()
    resp = client.post(
        "/duty-records",
        json={
            "personnel_certificate_number": certificate,
            "workstation_id": workstation_id,
            "start_time": f"{day}T08:00:00",
            "end_time": f"{day}T12:00:00",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["workstation_id"] == workstation_id


def test_step08_overlap_rejected(client, admin_headers):
    _, certificate, workstation_id = _create_chain(client, admin_headers)
    day = _future_day()
    base = {
        "personnel_certificate_number": certificate,
        "workstation_id": workstation_id,
    }
    assert (
        client.post(
            "/duty-records",
            json={
                **base,
                "start_time": f"{day}T08:00:00",
                "end_time": f"{day}T12:00:00",
            },
            headers=admin_headers,
        ).status_code
        == 201
    )
    resp = client.post(
        "/duty-records",
        json={
            **base,
            "start_time": f"{day}T11:00:00",
            "end_time": f"{day}T13:00:00",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 400


def test_step09_yearly_stats(client, admin_headers):
    _, certificate, workstation_id = _create_chain(client, admin_headers)
    day = _future_day()
    assert (
        client.post(
            "/duty-records",
            json={
                "personnel_certificate_number": certificate,
                "workstation_id": workstation_id,
                "start_time": f"{day}T08:00:00",
                "end_time": f"{day}T12:00:00",
            },
            headers=admin_headers,
        ).status_code
        == 201
    )
    resp = client.get(
        "/analytics/staff-duty-yearly",
        params={
            "personnel_certificate_number": certificate,
            "year": str(day.year),
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_duty_days"] == 1
    assert body["total_duty_hours"] == 4.0
    assert len(body["duty_by_month"]) == 12
    month = body["duty_by_month"][day.month - 1]
    assert month["days"] == 1
    assert month["hours"] == 4.0


def test_step10_time_distribution(client, admin_headers):
    _, certificate, workstation_id = _create_chain(client, admin_headers)
    day = _future_day()
    assert (
        client.post(
            "/duty-records",
            json={
                "personnel_certificate_number": certificate,
                "workstation_id": workstation_id,
                "start_time": f"{day}T08:00:00",
                "end_time": f"{day}T12:00:00",
            },
            headers=admin_headers,
        ).status_code
        == 201
    )
    resp = client.get(
        "/analytics/duty-time-distribution",
        params={
            "personnel_certificate_number": certificate,
            "year": str(day.year),
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["time_distribution"]) == 24
    assert body["total_records"] == 1
    assert body["time_distribution"][8]["count"] == 1
    assert body["peak_hours"] == [8]


def test_step11_me_requires_token(client):
    assert client.get("/users/me").status_code == 401


def test_step12_missing_field_is_422(client, admin_headers):
    resp = client.post(
        "/departments",
        json={"dept_code": _unique("D")},
        headers=admin_headers,
    )
    assert resp.status_code == 422
