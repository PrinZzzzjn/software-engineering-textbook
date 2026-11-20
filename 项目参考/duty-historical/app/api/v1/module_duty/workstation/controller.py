from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_active_user, get_current_admin_user
from app.api.v1.module_duty.workstation.service import workstation_service
from app.api.v1.module_duty.workstation.schema import (
    WorkstationCreate, WorkstationUpdate, WorkstationResponse
)
from app.api.v1.module_duty.workstation.param import WorkstationListParam

# 创建路由器
router = APIRouter(prefix="/workstation",tags=["工位管理"])


@router.post("/", response_model=WorkstationResponse, summary="创建工位", status_code=status.HTTP_201_CREATED)
async def create_workstation(
    *, db: Session = Depends(get_db), workstation_in: WorkstationCreate, current_user: dict = Depends(get_current_admin_user)
) -> Any:
    """
    创建新工位
    
    - **workstation_id**: 工位ID，必填，字符串类型
    - **workstation_name**: 工位名称，必填，字符串类型
    - **dept_code**: 单位内码，必填，字符串类型
    - **category_code**: 类别代码，可选，字符串类型
    - **longitude**: 经度，可选，浮点数类型
    - **latitude**: 纬度，可选，浮点数类型
    - **remark**: 备注，可选，字符串类型
    """
    workstation = workstation_service.create_workstation(db=db, obj_in=workstation_in)
    return workstation


@router.get("/{workstation_id}", response_model=WorkstationResponse, summary="获取单个工位信息")
async def get_workstation(
    *, db: Session = Depends(get_db), workstation_id: str, current_user: dict = Depends(get_current_active_user)
) -> Any:
    """
    根据工位ID获取工位详细信息
    
    - **workstation_id**: 工位ID，路径参数
    """
    workstation = workstation_service.get_workstation(db=db, workstation_id=workstation_id)
    return workstation


@router.put("/{workstation_id}", response_model=WorkstationResponse, summary="更新工位信息")
async def update_workstation(
    *, db: Session = Depends(get_db), workstation_id: str, workstation_in: WorkstationUpdate, current_user: dict = Depends(get_current_admin_user)
) -> Any:
    """
    更新工位信息
    
    - **workstation_id**: 工位ID，路径参数
    - **workstation_name**: 工位名称，可选，字符串类型
    - **dept_code**: 单位内码，可选，字符串类型
    - **category_code**: 类别代码，可选，字符串类型
    - **longitude**: 经度，可选，浮点数类型
    - **latitude**: 纬度，可选，浮点数类型
    - **remark**: 备注，可选，字符串类型
    """
    workstation = workstation_service.update_workstation(
        db=db, workstation_id=workstation_id, obj_in=workstation_in
    )
    return workstation


@router.delete("/{workstation_id}", response_model=Dict[str, str], summary="删除工位")
async def delete_workstation(
    *, db: Session = Depends(get_db), workstation_id: str, current_user: dict = Depends(get_current_admin_user)
) -> Any:
    """
    删除工位
    
    - **workstation_id**: 工位ID，路径参数
    """
    result = workstation_service.delete_workstation(db=db, workstation_id=workstation_id)
    return result


@router.get("/", response_model=Dict[str, Any], summary="获取工位列表")
async def get_workstation_list(
    *, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    workstation_name: str = Query(None, description="工位名称，支持模糊搜索"),
    dept_code: str = Query(None, description="单位内码"),
    category_code: str = Query(None, description="类别代码"),
    sort_by: str = Query("create_time", description="排序字段"),
    order: str = Query("desc", regex="^(asc|desc)$", description="排序方向，asc升序，desc降序")
) -> Any:
    """
    获取工位列表，支持分页、筛选和排序
    
    - **page**: 页码，默认1，最小值1
    - **page_size**: 每页数量，默认10，最小值1，最大值100
    - **workstation_name**: 工位名称，支持模糊搜索
    - **dept_code**: 单位内码，字符串类型
    - **category_code**: 类别代码，字符串类型
    - **sort_by**: 排序字段，默认create_time
    - **order**: 排序方向，asc升序，desc降序，默认desc
    """
    params = {
        "page": page,
        "page_size": page_size,
        "workstation_name": workstation_name,
        "dept_code": dept_code,
        "category_code": category_code,
        "sort_by": sort_by,
        "order": order
    }
    result = workstation_service.get_workstation_list(db=db, params=params)
    return result