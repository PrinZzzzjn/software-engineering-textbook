"""接口层：只取参数、调用 service、返回结果。请补全五个路由函数。

补完后启动 main.py，打开 /docs 应看到五个单位端点。
自检：python -c "from main import app; print(sorted(r.path for r in app.routes if r.path.startswith('/departments')))"
"""

from fastapi import APIRouter

from . import param, schema, service

router = APIRouter(prefix="/departments", tags=["单位"])

# TODO: 在下面登记五个接口，写法见教材 4.5 代码 4-5-7。
# GET    ""                 列表，用 params: param.DepartmentQueryParams = Depends() 注入查询参数
# GET    "/{dept_code}"     详情，200 / 404
# POST   ""                 新增，201 / 400 / 422
# PUT    "/{dept_code}"     修改，200 / 404 / 422
# DELETE "/{dept_code}"     删除，204 / 404
