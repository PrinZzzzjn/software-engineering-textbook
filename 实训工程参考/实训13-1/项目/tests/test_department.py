import uuid


def test_create_department_duplicate(client, admin_headers):
    payload = {
        "dept_code": f"D-{uuid.uuid4().hex[:6]}",
        "full_name": "测试单位",
    }
    assert (
        client.post(
            "/departments", json=payload, headers=admin_headers
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/departments", json=payload, headers=admin_headers
        ).status_code
        == 400
    )
