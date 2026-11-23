"""单位模块的业务规则（教材 6.2）。"""

from fastapi import HTTPException

from . import crud, model, schema


def list_departments(db, page: int, page_size: int) -> dict:
    offset = (page - 1) * page_size
    items, total = crud.list_page(db, offset, page_size)
    return {"items": items, "total": total}


def get_department(db, dept_code: str) -> model.Department:
    item = crud.get(db, dept_code)
    if item is None:
        raise HTTPException(status_code=404, detail="单位不存在")
    return item


def create_department(db, data: schema.DepartmentCreate) -> model.Department:
    if crud.get(db, data.dept_code) is not None:
        raise HTTPException(status_code=400, detail="单位编码已存在")
    return crud.create(db, model.Department(**data.model_dump()))


def update_department(db, dept_code: str, data: schema.DepartmentUpdate) -> model.Department:
    item = crud.get(db, dept_code)
    if item is None:
        raise HTTPException(status_code=404, detail="单位不存在")
    return crud.update(db, item, data.model_dump(exclude_unset=True))


def delete_department(db, dept_code: str) -> None:
    item = crud.get(db, dept_code)
    if item is None:
        raise HTTPException(status_code=404, detail="单位不存在")
    crud.delete(db, item)
