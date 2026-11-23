from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.department import service
from app.modules.department.param import DepartmentQueryParams
from app.modules.department.schema import DepartmentCreate, DepartmentOut

router = APIRouter(prefix="/departments", tags=["单位"])


@router.get("")
def list_departments(
    params: DepartmentQueryParams = Depends(),
    db: Session = Depends(get_db),
):
    return service.list_departments(db, params)


@router.post("", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(data: DepartmentCreate, db: Session = Depends(get_db)):
    return service.create_department(db, data)


@router.get("/{dept_code}", response_model=DepartmentOut)
def read_department(dept_code: str, db: Session = Depends(get_db)):
    return service.get_department(db, dept_code)


@router.put("/{dept_code}", response_model=DepartmentOut)
def update_department(
    dept_code: str, data: DepartmentCreate, db: Session = Depends(get_db)
):
    return service.update_department(db, dept_code, data)


@router.delete("/{dept_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(dept_code: str, db: Session = Depends(get_db)):
    service.delete_department(db, dept_code)
