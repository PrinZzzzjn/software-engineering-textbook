from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_admin_user, get_current_user
from app.core.base_schema import PaginatedResponse
from app.api.v1.module_duty.dept.schema import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse, 
    DepartmentDetailResponse, DepartmentListItem, DepartmentTree
)
from app.api.v1.module_duty.dept.param import DepartmentQueryParams
from app.api.v1.module_duty.dept.service import dept_service

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[DepartmentListItem],summary="获取部门列表")
def get_departments(
    params: DepartmentQueryParams = Depends(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取部门列表"""
    result = dept_service.get_department_list(db, params=params)
    
    # 转换为响应模型
    items = [
        DepartmentListItem(
            dept_code=dept.dept_code,
            full_name=dept.full_name,
            address=dept.address,
            longitude=dept.longitude,
            latitude=dept.latitude,
            parent_dept_code=dept.parent_dept_code,
            created_at=dept.create_time,
            updated_at=dept.update_time
        )
        for dept in result["items"]
    ]
    
    return PaginatedResponse[DepartmentListItem](
        items=items,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        pages=result["pages"]
    )

@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED,summary="创建新部门（仅管理员）")
def create_department(
    dept_in: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Any:
    """创建新部门（仅管理员）"""
    dept = dept_service.create_department(db, dept_in=dept_in)
    return DepartmentResponse(
        dept_code=dept.dept_code,
        full_name=dept.full_name,
        address=dept.address,
        longitude=dept.longitude,
        latitude=dept.latitude,
        parent_dept_code=dept.parent_dept_code,
        create_time=dept.create_time,
        update_time=dept.update_time
    )

@router.get("/tree", response_model=List[DepartmentTree],summary="获取部门树形结构")
def get_department_tree(
    root_dept_code: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取部门树形结构"""
    return dept_service.get_department_tree(db, root_dept_code=root_dept_code)

@router.get("/{dept_code}", response_model=DepartmentDetailResponse,summary="获取单个部门信息")
def get_department(
    dept_code: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取单个部门信息"""
    dept_detail = dept_service.get_department_detail(db, dept_code=dept_code)
    return DepartmentDetailResponse(**dept_detail)

@router.put("/{dept_code}", response_model=DepartmentResponse,summary="更新部门信息（仅管理员）")
def update_department(
    dept_code: str,
    dept_in: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Any:
    """更新部门信息（仅管理员）"""
    dept = dept_service.update_department(db, dept_code=dept_code, dept_in=dept_in)
    return DepartmentResponse(
        dept_code=dept.dept_code,
        full_name=dept.full_name,
        address=dept.address,
        longitude=dept.longitude,
        latitude=dept.latitude,
        parent_dept_code=dept.parent_dept_code,
        create_time=dept.create_time,
        update_time=dept.update_time
    )

@router.delete("/{dept_code}",summary="删除部门（仅管理员）")
def delete_department(
    dept_code: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """删除部门（仅管理员）"""
    dept_service.delete_department(db, dept_code=dept_code)
    return {"message": "部门删除成功"}