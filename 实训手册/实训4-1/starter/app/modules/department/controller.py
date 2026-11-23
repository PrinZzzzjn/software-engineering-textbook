"""接口层：只取参数、调用 service、返回结果。课堂 B 档只登记两个路由函数。

补完后启动 main.py，打开 /docs 应看到 GET 列表与 POST 新增两个端点。
自检：python -c "from main import app; print(sorted(r.path for r in app.routes if r.path.startswith('/departments')))"
"""

from fastapi import APIRouter

from . import param, schema, service

router = APIRouter(prefix="/departments", tags=["单位"])

# TODO: B 档只登记下面两个接口；其余三条由教师演示。
# GET    ""                 列表，用 params: param.DepartmentQueryParams = Depends() 注入查询参数
# POST   ""                 新增，201 / 400 / 422
