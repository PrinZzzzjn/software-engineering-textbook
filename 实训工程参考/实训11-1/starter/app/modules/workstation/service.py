from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.department.crud import get_by_code as get_dept_by_code
from app.modules.workstation import crud


def _ensure_dept_exists(db: Session, dept_code: str):
    if not get_dept_by_code(db, dept_code):
        raise HTTPException(status_code=400, detail="所属单位不存在")


def list_workstations(db, params):
    offset = (params.page - 1) * params.page_size
    items, total = crud.list_page(db, offset, params.page_size, params.dept_code)
    return {"items": items, "total": total}


def create_workstation(db, data):
    if crud.get_by_id(db, data.workstation_id):
        raise HTTPException(status_code=400, detail="哨位编号已存在")
    _ensure_dept_exists(db, data.dept_code)
    return crud.create(db, data)


def get_workstation(db, workstation_id: str):
    workstation = crud.get_by_id(db, workstation_id)
    if not workstation:
        raise HTTPException(status_code=404, detail="哨位不存在")
    return workstation


def update_workstation(db, workstation_id: str, data):
    workstation = crud.get_by_id(db, workstation_id)
    if not workstation:
        raise HTTPException(status_code=404, detail="哨位不存在")
    payload = data.model_dump(exclude_unset=True)
    if "dept_code" in payload:
        _ensure_dept_exists(db, payload["dept_code"])
    return crud.update(db, workstation, payload)


def delete_workstation(db, workstation_id: str) -> None:
    workstation = crud.get_by_id(db, workstation_id)
    if not workstation:
        raise HTTPException(status_code=404, detail="哨位不存在")
    crud.delete(db, workstation)
