from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db

from . import param, schema, service

router = APIRouter(prefix="/departments", tags=["单位"])


@router.get("", response_model=schema.DepartmentPage)
def list_departments(
    params: param.DeptQuery = Depends(), db: Session = Depends(get_db)
):
    return service.list_departments(db, params.page, params.page_size)


@router.get("/{dept_code}", response_model=schema.DepartmentOut)
def get_department(dept_code: str, db: Session = Depends(get_db)):
    return service.get_department(db, dept_code)


@router.post(
    "", response_model=schema.DepartmentOut, status_code=status.HTTP_201_CREATED
)
def create_department(data: schema.DepartmentCreate, db: Session = Depends(get_db)):
    return service.create_department(db, data)


@router.put("/{dept_code}", response_model=schema.DepartmentOut)
def update_department(
    dept_code: str, data: schema.DepartmentUpdate, db: Session = Depends(get_db)
):
    return service.update_department(db, dept_code, data)


@router.delete("/{dept_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(dept_code: str, db: Session = Depends(get_db)):
    service.delete_department(db, dept_code)
