from fastapi import FastAPI

app = FastAPI()

DEPARTMENTS = {
    "D01": {"dept_code": "D01", "full_name": "一中队", "address": "一号楼"},
}


@app.get("/departments")
def list_departments():
    return {"items": list(DEPARTMENTS.values()), "total": len(DEPARTMENTS)}


# TODO 1：补 GET /departments/{dept_code}，不存在时返回 404
# TODO 2：补 POST /departments，成功返回 201，缺字段或编码重复返回 400
# TODO 3：补 PUT /departments/{dept_code}，成功返回 200，不存在返回 404
# TODO 4：补 DELETE /departments/{dept_code}，成功返回 204，不存在返回 404
