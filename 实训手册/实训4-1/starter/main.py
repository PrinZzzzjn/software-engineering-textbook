"""综合实训 4-1 骨架：最小可运行的 FastAPI 应用（示例模块：工位）。

案例背景：执勤电子年鉴。部门下设工位，一个部门有多个工位，一个工位只属于一个部门；
值班记录再挂到工位上。本文件实现工位的三个接口，是第 4 章模块模板的最小落地。

对应教材：第 3 章 3.4（APIRouter 与 include_router）、3.5（输入模型与 HTTPException）、
          第 4 章 4.4（接口组）、4.5（模块模板中的 controller.py 职责）。

本文件只演示机制，不是可提交的答案：
  - 列表接口已完成，可直接看到 200 与 items / total 的返回结构；
  - 新增、查询单个两处标有 TODO，对应实训手册的步骤 5；
  - 修改与删除只出现在设计文档的接口清单中，本实训不实现；
  - 用内存列表代替数据库；model.py 与 crud.py 留到第 8 章。

提交时须替换为自己选定的业务对象，并把设计文档中的表、接口、目录三节同步改过来。
"""

from fastapi import APIRouter, FastAPI, HTTPException

from schemas import WorkstationCreate, WorkstationListOut, WorkstationOut

# 应用对象：所有路由最终都挂在它上面，/docs 页面也由它生成。
app = FastAPI(
    title="综合实训 4-1 骨架（工位示例）",
    description="最小实现：列表接口已完成，其余接口见代码中的 TODO",
    version="0.1.0",
)

# 模块级挂载点：模块 prefix 与 include_router 的 prefix 相加才是完整路径。
# 资源名为可数名词复数（workstations），与第 4 章 4.4 的接口组表一致。
# 集合路径统一带尾斜杠；FastAPI 对另一种写法会做 307 重定向，但不应依赖该重定向，
# 设计文档与代码须写成同一形式。
router = APIRouter(prefix="/api/v1/workstations", tags=["工位（示例）"])

# 内存列表演示“一张表”。第 8 章把这里换成 model.py + crud.py + 真实数据库。
items: list[dict] = [
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


# 查询集合：成功状态码 200。response_model 会在返回前按输出模型过滤字段。
@router.get("/", response_model=WorkstationListOut, summary="查询工位列表")
def list_workstations():
    """已完成：返回全部记录，状态码 200。"""
    return {"items": items, "total": len(items)}


# 新增：成功状态码 201。请求体先由 WorkstationCreate 校验，不合法时框架在进入函数前返回 422。
@router.post("/", status_code=201, response_model=WorkstationOut, summary="新增工位")
def create_workstation(data: WorkstationCreate):
    """TODO（步骤 5）：把新增记录写入 items。

    要求：把记录加入 items，返回该记录，状态码 201。
    可选：工位编号已存在时 raise HTTPException(status_code=400, detail="工位编号已存在")。
    当前实现只把输入原样返回，未写入 items。
    """
    return data


# 查询单个：200 / 404。路径参数用于定位一条记录；找不到时由函数内抛出的 HTTPException 拒绝。
@router.get("/{workstation_id}", response_model=WorkstationOut, summary="查询单个工位")
def get_workstation(workstation_id: str):
    """TODO（步骤 5）：按编号查找；找不到时返回 404。

    要求：先在 items 中查找；找不到时
          raise HTTPException(status_code=404, detail="工位不存在")
    当前实现固定返回占位记录，因此任何编号都会得到 200。
    """
    return {
        "workstation_id": workstation_id,
        "workstation_name": "待实现",
        "dept_code": "D01",
        "category_code": None,
        "remark": None,
    }


# 把模块路由挂到应用。本例的完整路径已由 router 的 prefix 给出，此处不再追加前缀。
app.include_router(router)
