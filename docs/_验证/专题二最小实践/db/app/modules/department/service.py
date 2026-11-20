from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import crud, model, schema


def list_departments(db: Session, page: int, page_size: int) -> dict:
    items = crud.list_all(db)
    start = (page - 1) * page_size
    page_items = items[start : start + page_size]
    return {
        "items": [schema.DepartmentOut.model_validate(item) for item in page_items],
        "total": len(items),
    }


def get_department(db: Session, dept_code: str) -> model.Department:
    item = crud.get(db, dept_code)
    if item is None:
        raise HTTPException(status_code=404, detail="部门不存在")
    return item


def create_department(
    db: Session, data: schema.DepartmentCreate
) -> model.Department:
    if crud.get(db, data.dept_code) is not None:
        raise HTTPException(status_code=400, detail="部门编码已存在")
    return crud.create(db, model.Department(**data.model_dump()))


def update_department(
    db: Session, dept_code: str, data: schema.DepartmentUpdate
) -> model.Department:
    item = crud.get(db, dept_code)
    if item is None:
        raise HTTPException(status_code=404, detail="部门不存在")
    return crud.update(db, item, data.model_dump(exclude_unset=True))


def delete_department(db: Session, dept_code: str) -> None:
    item = crud.get(db, dept_code)
    if item is None:
        raise HTTPException(status_code=404, detail="部门不存在")
    crud.delete(db, item)
