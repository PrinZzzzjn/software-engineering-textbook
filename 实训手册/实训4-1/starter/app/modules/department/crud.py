"""数据读写：只存取，不判断业务规则。请补全五个函数。"""

from . import model


def list_all():
    raise NotImplementedError("补全 crud.list_all")


def get(dept_code: str):
    raise NotImplementedError("补全 crud.get")


def create(item: model.Department):
    raise NotImplementedError("补全 crud.create")


def update(item: model.Department, data: dict):
    raise NotImplementedError("补全 crud.update")


def delete(item: model.Department):
    raise NotImplementedError("补全 crud.delete")
