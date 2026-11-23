"""数据读写：只存取，不判断业务规则。课堂 B 档只补 list_all / create。

先补两个函数，再运行：
python -c "from app.modules.department import crud, model; item=crud.create(model.Department('D01','一中队')); print(crud.list_all())"
"""

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
