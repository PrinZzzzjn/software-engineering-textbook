"""教材 13.1～13.3 的质量清单：安全、错误、重复、性能、规范各留下可重跑的用例。"""

import random
import uuid
from datetime import date, timedelta

import pytest
from fastapi import HTTPException

from app.modules.duty_record import service
from app.modules.duty_record.model import DutyRecord
from app.modules.duty_record.schema import DutyRecordCreate


def _unique(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex[:6].upper()}"


def _future_day() -> date:
    return date.today() + timedelta(days=random.randint(3000, 4000))


def _create_chain(client, admin_headers):
    dept_code = _unique("D")
    certificate = _unique("P")
    workstation_id = _unique("W")
    assert (
        client.post(
            "/departments",
            json={"dept_code": dept_code, "full_name": "质检测试单位"},
            headers=admin_headers,
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/personnel",
            json={
                "certificate_number": certificate,
                "name": "质检测试人员",
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
                "name": "质检测试哨位",
                "dept_code": dept_code,
            },
            headers=admin_headers,
        ).status_code
        == 201
    )
    return dept_code, certificate, workstation_id


def _row(certificate: str, workstation_id: str, day: date, start: str, end: str):
    return DutyRecordCreate(
        personnel_certificate_number=certificate,
        workstation_id=workstation_id,
        start_time=f"{day}T{start}:00",
        end_time=f"{day}T{end}:00",
    )


def _record_count(db, workstation_id: str) -> int:
    return (
        db.query(DutyRecord)
        .filter(DutyRecord.workstation_id == workstation_id)
        .count()
    )


# ---------- 安全 ----------


def test_user_response_has_no_password_hash(client, admin_headers):
    """响应裁剪：注册与列表都不出现 password_hash。"""
    username = f"leak_{uuid.uuid4().hex[:8]}"
    created = client.post(
        "/users", json={"username": username, "password": "secret123"}
    )
    assert created.status_code == 201
    assert "password_hash" not in created.json()

    listing = client.get(
        "/users", params={"page": 1, "page_size": 100}, headers=admin_headers
    )
    assert listing.status_code == 200
    target = next(
        item for item in listing.json()["items"] if item["username"] == username
    )
    assert set(target) == {"id", "username", "role", "is_active"}


# ---------- 错误 ----------


def test_error_400_duplicate_department(client, admin_headers):
    payload = {"dept_code": _unique("D"), "full_name": "重复单位"}
    assert (
        client.post(
            "/departments", json=payload, headers=admin_headers
        ).status_code
        == 201
    )
    resp = client.post("/departments", json=payload, headers=admin_headers)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "单位编码已存在"


def test_error_401_without_token(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401
    assert "detail" in resp.json()


def test_error_403_normal_user(client, normal_headers):
    resp = client.get("/users", headers=normal_headers)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "权限不足"


def test_error_404_missing_department(client):
    resp = client.get("/departments/NOT-EXIST")
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_error_422_invalid_body(client, admin_headers):
    resp = client.post(
        "/departments",
        json={"dept_code": _unique("D")},
        headers=admin_headers,
    )
    assert resp.status_code == 422
    assert "detail" in resp.json()


# ---------- 规范 ----------


def test_all_list_endpoints_share_items_total(client, admin_headers):
    for path in ("/departments", "/personnel", "/workstations", "/duty-records"):
        resp = client.get(path, params={"page": 1, "page_size": 10})
        assert resp.status_code == 200
        assert set(resp.json()) == {"items", "total"}

    resp = client.get(
        "/users", params={"page": 1, "page_size": 10}, headers=admin_headers
    )
    assert resp.status_code == 200
    assert set(resp.json()) == {"items", "total"}


# ---------- 事务 ----------


def test_batch_write_atomic_when_one_row_invalid(
    client, admin_headers, db_session
):
    """批量中有一条人员不存在：整批不写，数据库没有半批数据。"""
    _, certificate, workstation_id = _create_chain(client, admin_headers)
    day = _future_day()
    valid = _row(certificate, workstation_id, day, "08:00", "12:00")
    invalid = _row("NOT-EXIST", workstation_id, day, "13:00", "16:00")

    with pytest.raises(HTTPException) as exc:
        service.create_duty_records(db_session, [valid, invalid])

    assert exc.value.status_code == 400
    assert _record_count(db_session, workstation_id) == 0


def test_batch_write_commits_all_rows(client, admin_headers, db_session):
    """全部合法：一次事务写入两条，两条都有主键。"""
    _, certificate, workstation_id = _create_chain(client, admin_headers)
    day = _future_day()
    first = _row(certificate, workstation_id, day, "08:00", "10:00")
    second = _row(certificate, workstation_id, day, "10:00", "12:00")

    records = service.create_duty_records(db_session, [first, second])

    assert len(records) == 2
    assert all(record.id for record in records)
    assert _record_count(db_session, workstation_id) == 2


def test_batch_internal_overlap_rejected(client, admin_headers, db_session):
    """批内两条时段重叠：在写入前拒绝，数据库为空。"""
    _, certificate, workstation_id = _create_chain(client, admin_headers)
    day = _future_day()
    first = _row(certificate, workstation_id, day, "08:00", "12:00")
    second = _row(certificate, workstation_id, day, "11:00", "13:00")

    with pytest.raises(HTTPException) as exc:
        service.create_duty_records(db_session, [first, second])

    assert exc.value.status_code == 400
    assert "同一批次" in exc.value.detail
    assert _record_count(db_session, workstation_id) == 0
