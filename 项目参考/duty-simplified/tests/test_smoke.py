import uuid

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_departments_list():
    r = client.get("/departments")
    assert r.status_code == 200
    assert "items" in r.json()
    assert "total" in r.json()


def test_department_crud():
    # 新增
    r = client.post(
        "/departments",
        json={"dept_code": "D001", "full_name": "一中队", "address": "一号营区"},
    )
    assert r.status_code == 201

    # 重复
    r = client.post(
        "/departments",
        json={"dept_code": "D001", "full_name": "一中队"},
    )
    assert r.status_code == 400

    # 详情
    r = client.get("/departments/D001")
    assert r.status_code == 200
    assert r.json()["dept_code"] == "D001"

    # 不存在的编码
    r = client.get("/departments/D404")
    assert r.status_code == 404

    # 删除
    r = client.delete("/departments/D001")
    assert r.status_code == 204


def test_analytics():
    suffix = uuid.uuid4().hex[:6]
    dept, cert, ws = f"D{suffix}", f"P{suffix}", f"W{suffix}"

    assert client.post(
        "/departments",
        json={"dept_code": dept, "full_name": "统计测试单位"},
    ).status_code == 201
    assert client.post(
        "/personnel",
        json={"certificate_number": cert, "name": "统计测试人员", "dept_code": dept},
    ).status_code == 201
    assert client.post(
        "/workstations",
        json={"workstation_id": ws, "name": "统计测试哨位", "dept_code": dept},
    ).status_code == 201

    records = [
        ("2026-01-05T08:00:00", "2026-01-05T12:00:00"),
        ("2026-01-05T13:00:00", "2026-01-05T17:00:00"),
    ]
    for start, end in records:
        assert client.post(
            "/duty-records",
            json={
                "personnel_certificate_number": cert,
                "workstation_id": ws,
                "start_time": start,
                "end_time": end,
            },
        ).status_code == 201

    # 年度统计：同一天两条记录算 1 天、时长累加
    r = client.get(
        "/analytics/staff-duty-yearly",
        params={"personnel_certificate_number": cert, "year": "2026"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total_duty_days"] == 1
    assert body["total_duty_hours"] == 8.0
    assert len(body["duty_by_month"]) == 12
    assert body["duty_by_month"][0] == {"month": 1, "days": 1, "hours": 8.0}

    # 时段分布：补齐 24 项，高峰并列
    r = client.get(
        "/analytics/duty-time-distribution",
        params={"personnel_certificate_number": cert, "year": "2026"},
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body["time_distribution"]) == 24
    assert body["peak_hours"] == [8, 13]
    assert body["total_records"] == 2

    # 输入检查：年份格式错误、人员不存在均为 400
    assert client.get(
        "/analytics/staff-duty-yearly",
        params={"personnel_certificate_number": cert, "year": "26"},
    ).status_code == 400
    assert client.get(
        "/analytics/staff-duty-yearly",
        params={"personnel_certificate_number": "P-NOBODY", "year": "2026"},
    ).status_code == 400
