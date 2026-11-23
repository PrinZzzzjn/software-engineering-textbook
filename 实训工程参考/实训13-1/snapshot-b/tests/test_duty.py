import random
from datetime import date, timedelta


def test_duty_record_touching(client, admin_headers):
    """前一段 12:00 结束、后一段 12:00 开始，首尾相接不算冲突。"""
    day = date.today() + timedelta(days=random.randint(1000, 2000))
    base = {"personnel_certificate_number": "P001", "workstation_id": "W001"}
    first = {**base, "start_time": f"{day}T08:00:00", "end_time": f"{day}T12:00:00"}
    second = {**base, "start_time": f"{day}T12:00:00", "end_time": f"{day}T14:00:00"}
    assert (
        client.post("/duty-records", json=first, headers=admin_headers).status_code
        == 201
    )
    assert (
        client.post("/duty-records", json=second, headers=admin_headers).status_code
        == 201
    )


def test_duty_record_overlap(client, admin_headers):
    """例 12-1：08:00–12:00 之后再来 11:00–13:00，应返回 400。"""
    day = date.today() + timedelta(days=random.randint(1000, 2000))
    base = {"personnel_certificate_number": "P001", "workstation_id": "W001"}
    first = {**base, "start_time": f"{day}T08:00:00", "end_time": f"{day}T12:00:00"}
    second = {**base, "start_time": f"{day}T11:00:00", "end_time": f"{day}T13:00:00"}
    assert (
        client.post("/duty-records", json=first, headers=admin_headers).status_code
        == 201
    )
    assert (
        client.post("/duty-records", json=second, headers=admin_headers).status_code
        == 400
    )
