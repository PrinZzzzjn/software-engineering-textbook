"""业务规则：编码重复返回 400，资源不存在返回 404。请补全五个函数。"""

from . import crud, model, schema


def list_departments(page: int, page_size: int) -> dict:
    raise NotImplementedError("补全 service.list_departments")


def get_department(dept_code: str) -> model.Department:
    raise NotImplementedError("补全 service.get_department")


def create_department(data: schema.DepartmentCreate) -> model.Department:
    raise NotImplementedError("补全 service.create_department")


def update_department(
    dept_code: str, data: schema.DepartmentUpdate
) -> model.Department:
    raise NotImplementedError("补全 service.update_department")


def delete_department(dept_code: str) -> None:
    raise NotImplementedError("补全 service.delete_department")
