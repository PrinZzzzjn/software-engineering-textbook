from fastapi import APIRouter, Depends, status

from . import param, schema, service

router = APIRouter(prefix="/departments", tags=["单位"])


@router.get("", response_model=schema.DepartmentPage)
def list_departments(params: param.DepartmentQueryParams = Depends()):
    return service.list_departments(params.page, params.page_size)


@router.get("/{dept_code}", response_model=schema.DepartmentOut)
def get_department(dept_code: str):
    return service.get_department(dept_code)


@router.post(
    "", response_model=schema.DepartmentOut, status_code=status.HTTP_201_CREATED
)
def create_department(data: schema.DepartmentCreate):
    return service.create_department(data)


@router.put("/{dept_code}", response_model=schema.DepartmentOut)
def update_department(dept_code: str, data: schema.DepartmentUpdate):
    return service.update_department(dept_code, data)


@router.delete("/{dept_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(dept_code: str):
    service.delete_department(dept_code)
