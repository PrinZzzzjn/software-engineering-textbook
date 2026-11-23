from fastapi import HTTPException

from app.modules.department import crud


def list_departments(db, params):
    offset = (params.page - 1) * params.page_size
    items, total = crud.list_page(db, offset, params.page_size, params.full_name)
    return {"items": items, "total": total}


def create_department(db, data):
    if crud.get_by_code(db, data.dept_code):
        raise HTTPException(status_code=400, detail="单位编码已存在")
    return crud.create(db, data)


def get_department(db, dept_code: str):
    department = crud.get_by_code(db, dept_code)
    if not department:
        raise HTTPException(status_code=404, detail="单位不存在")
    return department


def update_department(db, dept_code: str, data):
    department = crud.get_by_code(db, dept_code)
    if not department:
        raise HTTPException(status_code=404, detail="单位不存在")
    return crud.update(db, department, data.model_dump(exclude_unset=True))


def delete_department(db, dept_code: str) -> None:
    department = crud.get_by_code(db, dept_code)
    if not department:
        raise HTTPException(status_code=404, detail="单位不存在")
    crud.delete(db, department)
