from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin_user
from app.modules.department import service
from app.modules.department.param import DepartmentQueryParams
from app.modules.department.schema import (
    DepartmentCreate,
    DepartmentOut,
    DepartmentPage,
    DepartmentUpdate,
)

router = APIRouter(prefix="/departments", tags=["单位"])


@router.get("", response_model=DepartmentPage)
def list_departments(
    params: DepartmentQueryParams = Depends(),
    db: Session = Depends(get_db),
):
    return service.list_departments(db, params)


@router.post(
    "",
    response_model=DepartmentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)],
)
def create_department(data: DepartmentCreate, db: Session = Depends(get_db)):
    return service.create_department(db, data)


@router.get("/{dept_code}", response_model=DepartmentOut)
def read_department(dept_code: str, db: Session = Depends(get_db)):
    return service.get_department(db, dept_code)


@router.put(
    "/{dept_code}",
    response_model=DepartmentOut,
    dependencies=[Depends(get_current_admin_user)],
)
def update_department(
    dept_code: str, data: DepartmentUpdate, db: Session = Depends(get_db)
):
    return service.update_department(db, dept_code, data)


@router.delete(
    "/{dept_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin_user)],
)
def delete_department(dept_code: str, db: Session = Depends(get_db)):
    service.delete_department(db, dept_code)
