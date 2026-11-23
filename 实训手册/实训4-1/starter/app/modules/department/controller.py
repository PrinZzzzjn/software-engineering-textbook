from fastapi import APIRouter

from . import param, schema, service

router = APIRouter(prefix="/departments", tags=["单位"])

# TODO: 在下面登记五个接口，写法见教材 4.6 代码 4-6-7。
# GET    ""                 列表，用 params: param.DepartmentQueryParams = Depends() 注入查询参数
# GET    "/{dept_code}"     详情，200 / 404
# POST   ""                 新增，201 / 400 / 422
# PUT    "/{dept_code}"     修改，200 / 404 / 422
# DELETE "/{dept_code}"     删除，204 / 404
