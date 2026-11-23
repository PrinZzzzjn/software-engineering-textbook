from fastapi import APIRouter, Depends, status

from . import param, schema, service

router = APIRouter(prefix="/departments", tags=["单位"])


@router.get("", response_model=schema.DepartmentPage)
def list_departments(params: param.DepartmentQueryParams = Depends()):
    return service.list_departments(params.page, params.page_size)


@router.post(
    "", response_model=schema.DepartmentOut, status_code=status.HTTP_201_CREATED
)
def create_department(data: schema.DepartmentCreate):
    return service.create_department(data)
