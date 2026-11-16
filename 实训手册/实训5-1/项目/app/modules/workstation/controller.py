"""工位模块的接口层（controller）：接请求、取参数、返回响应。

由第 4 章实训 4-1 的 main.py 迁入：应用留在根目录 main.py，接口归本文件。
本文件只处理接口；业务规则与数据库读写在第 8 章加入 service.py 与 crud.py。
"""

from fastapi import APIRouter, HTTPException

from app.modules.workstation.schema import (
    WorkstationCreate,
    WorkstationListOut,
    WorkstationOut,
)

# 模块级路由：前缀只写本资源名，"/api/v1" 由根目录 main.py 的 include_router 提供。
router = APIRouter(prefix="/workstations", tags=["工位"])

# 内存数据演示“一张表”：第 8 章换成 model.py + crud.py + 真实数据库。
items = [
    {
        "workstation_id": "WS-001",
        "workstation_name": "一号值班台",
        "dept_code": "D01",
        "category_code": "C01",
        "remark": None,
    },
    {
        "workstation_id": "WS-002",
        "workstation_name": "二号值班台",
        "dept_code": "D02",
        "category_code": "C02",
        "remark": None,
    },
]


# 查询集合：成功状态码 200；response_model 会在返回前按输出模型过滤字段。
@router.get("/", response_model=WorkstationListOut)
def list_workstations():
    return {"items": items, "total": len(items)}


# 新增：成功状态码 201；请求体先由 WorkstationCreate 校验，不合法时框架在进入函数前返回 422。
@router.post("/", status_code=201, response_model=WorkstationOut)
def create_workstation(data: WorkstationCreate):
    items.append(data.model_dump())  # model_dump() 把模型转成字典，才能放进列表
    return data


# 查询单个：200 / 404；路径参数用于定位一条记录，找不到时由 HTTPException 拒绝。
@router.get("/{workstation_id}", response_model=WorkstationOut)
def get_workstation(workstation_id: str):
    for item in items:
        if item["workstation_id"] == workstation_id:
            return item
    raise HTTPException(status_code=404, detail="工位不存在")
