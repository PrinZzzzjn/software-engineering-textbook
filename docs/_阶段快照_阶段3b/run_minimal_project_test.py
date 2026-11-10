# -*- coding: utf-8 -*-
"""最小工程实跑校验：按第 5 章 5.9 印刷的 main.py / schemas.py / deps.py 原样运行。

用法：python docs/_验证/run_minimal_project_test.py
"""
import sys
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE / "最小工程"
sys.path.insert(0, str(PROJECT))

from fastapi.testclient import TestClient  # noqa: E402
import main  # noqa: E402

client = TestClient(main.app)
results = []


def check(name, resp, status, predicate=None):
    ok = resp.status_code == status
    if ok and predicate is not None:
        ok = predicate(resp)
    results.append((name, ok, resp.status_code, resp.text[:200]))
    return ok


check("GET /health", client.get("/health"), 200,
      lambda r: r.json() == {"status": "ok"})
check("GET /api/v1/departments", client.get("/api/v1/departments"), 200,
      lambda r: len(r.json()) == 2)
check("POST 合法请求", client.post("/api/v1/departments",
      json={"dept_code": "D03", "dept_name": "三中队"}), 201)
check("POST 非法请求（dept_code 太短）", client.post("/api/v1/departments",
      json={"dept_code": "D", "dept_name": "三中队"}), 422)
check("DELETE 不存在资源", client.delete("/api/v1/departments/999"), 404)
check("GET /docs", client.get("/docs"), 200)

failed = [r for r in results if not r[1]]
for name, ok, status, body in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}  -> {status}  {body}")
print(f"\n{len(results) - len(failed)}/{len(results)} PASS")
sys.exit(1 if failed else 0)
