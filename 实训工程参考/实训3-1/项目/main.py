from fastapi import FastAPI, HTTPException, status

app = FastAPI()

DEPARTMENTS = {
    "D01": {"dept_code": "D01", "full_name": "一中队", "address": "一号楼"},
}


@app.get("/departments")
def list_departments():
    return {"items": list(DEPARTMENTS.values()), "total": len(DEPARTMENTS)}


@app.get("/departments/{dept_code}")
def get_department(dept_code: str):
    if dept_code not in DEPARTMENTS:
        raise HTTPException(status_code=404, detail="单位不存在")
    return DEPARTMENTS[dept_code]


@app.post("/departments", status_code=status.HTTP_201_CREATED)
def create_department(data: dict):
    dept_code = data.get("dept_code")
    full_name = data.get("full_name")
    if not dept_code or not full_name:
        raise HTTPException(status_code=400, detail="缺少必填字段")
    if dept_code in DEPARTMENTS:
        raise HTTPException(status_code=400, detail="单位编码已存在")
    DEPARTMENTS[dept_code] = {
        "dept_code": dept_code,
        "full_name": full_name,
        "address": data.get("address"),
    }
    return DEPARTMENTS[dept_code]


@app.put("/departments/{dept_code}")
def update_department(dept_code: str, data: dict):
    if dept_code not in DEPARTMENTS:
        raise HTTPException(status_code=404, detail="单位不存在")
    item = DEPARTMENTS[dept_code]
    if "full_name" in data:
        item["full_name"] = data["full_name"]
    if "address" in data:
        item["address"] = data["address"]
    return item


@app.delete("/departments/{dept_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(dept_code: str):
    if dept_code not in DEPARTMENTS:
        raise HTTPException(status_code=404, detail="单位不存在")
    del DEPARTMENTS[dept_code]
