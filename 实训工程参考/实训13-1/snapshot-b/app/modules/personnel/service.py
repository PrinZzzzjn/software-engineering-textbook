from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.department.crud import get_by_code as get_dept_by_code
from app.modules.personnel import crud


def _ensure_dept_exists(db: Session, dept_code: str):
    if not get_dept_by_code(db, dept_code):
        raise HTTPException(status_code=400, detail="所属单位不存在")


def list_personnel(db, params):
    offset = (params.page - 1) * params.page_size
    items, total = crud.list_page(
        db, offset, params.page_size, params.name, params.dept_code
    )
    return {"items": items, "total": total}


def create_personnel(db, data):
    if crud.get_by_certificate_number(db, data.certificate_number):
        raise HTTPException(status_code=400, detail="证件号已存在")
    _ensure_dept_exists(db, data.dept_code)
    return crud.create(db, data)


def get_personnel(db, certificate_number: str):
    personnel = crud.get_by_certificate_number(db, certificate_number)
    if not personnel:
        raise HTTPException(status_code=404, detail="人员不存在")
    return personnel


def update_personnel(db, certificate_number: str, data):
    personnel = crud.get_by_certificate_number(db, certificate_number)
    if not personnel:
        raise HTTPException(status_code=404, detail="人员不存在")
    payload = data.model_dump(exclude_unset=True)
    if "dept_code" in payload:
        _ensure_dept_exists(db, payload["dept_code"])
    return crud.update(db, personnel, payload)


def delete_personnel(db, certificate_number: str) -> None:
    personnel = crud.get_by_certificate_number(db, certificate_number)
    if not personnel:
        raise HTTPException(status_code=404, detail="人员不存在")
    crud.delete(db, personnel)
