"""契约测试：同一组断言分别跑内存版与数据库版。

用法：
    python docs/_验证/专题二最小实践/run_contract_test.py --app memory
    python docs/_验证/专题二最小实践/run_contract_test.py --app db
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

parser = argparse.ArgumentParser()
parser.add_argument("--app", choices=["memory", "db"], required=True)
args = parser.parse_args()

sys.path.insert(0, str(ROOT / args.app))

from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)

results: list[bool] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    results.append(condition)
    mark = "PASS" if condition else "FAIL"
    line = f"{mark} {name}"
    if detail and not condition:
        line += f" -> {detail}"
    print(line)


prefix = "/api/v1/departments"

response = client.post(
    prefix, json={"dept_code": "D99", "full_name": "测试部门", "address": "一号楼"}
)
check("新增返回 201", response.status_code == 201, response.text)

response = client.post(
    prefix, json={"dept_code": "D99", "full_name": "重复部门", "address": None}
)
check("编码重复返回 400", response.status_code == 400, response.text)

response = client.get(prefix)
check(
    "列表返回 200",
    response.status_code == 200 and response.json().get("total", 0) >= 1,
    response.text,
)

response = client.get(f"{prefix}/D99")
check(
    "详情返回 200",
    response.status_code == 200 and response.json()["full_name"] == "测试部门",
    response.text,
)

response = client.put(f"{prefix}/D99", json={"full_name": "测试部门二"})
check(
    "修改返回 200",
    response.status_code == 200 and response.json()["full_name"] == "测试部门二",
    response.text,
)

response = client.get(f"{prefix}/D404")
check("详情不存在返回 404", response.status_code == 404, response.text)

response = client.put(f"{prefix}/D404", json={"full_name": "不存在"})
check("修改不存在返回 404", response.status_code == 404, response.text)

response = client.post(prefix, json={"dept_code": "D", "full_name": "短的"})
check("字段非法返回 422", response.status_code == 422, response.text)

response = client.delete(f"{prefix}/D99")
check(
    "删除返回 204 且无响应体",
    response.status_code == 204 and response.content == b"",
    f"{response.status_code} {response.text!r}",
)

response = client.delete(f"{prefix}/D99")
check("重复删除返回 404", response.status_code == 404, response.text)

passed = sum(results)
print(f"\n{args.app}: {passed}/{len(results)} PASS")
sys.exit(0 if passed == len(results) else 1)
