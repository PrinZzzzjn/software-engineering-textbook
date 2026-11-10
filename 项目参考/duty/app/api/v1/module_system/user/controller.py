from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_admin_user, get_current_user
from app.core.base_schema import PaginatedResponse
from app.api.v1.module_system.user.schema import (
    UserCreate, UserUpdate, UserResponse, ResetPasswordRequest,
    UserListItem
)
from app.api.v1.module_system.user.param import UserQueryParams
from app.api.v1.module_system.user.service import user_service

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[UserListItem],summary="获取用户列表（仅管理员）")
def get_users(
    params: UserQueryParams = Depends(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Any:
    """获取用户列表（仅管理员）"""
    result = user_service.get_user_list(db, params=params)
    
    # 转换为响应模型
    items = [
        UserListItem(
            id=user.id,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            personnel_id=user.personnel_id,
            created_at=user.create_time,
            updated_at=user.update_time
        )
        for user in result["items"]
    ]
    
    return PaginatedResponse(
        items=items,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        pages=result["pages"]
    )

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED,summary="创建新用户（仅管理员）")
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Any:
    """创建新用户（仅管理员）"""
    user = user_service.create_user(db, user_in=user_in)
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        personnel_id=user.personnel_id,
        create_time=user.create_time,
        update_time=user.update_time
    )

@router.get("/{user_id}", response_model=UserResponse,summary="获取单个用户信息（仅管理员）")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Any:
    """获取单个用户信息（仅管理员）"""
    user = user_service.get_user_by_id(db, user_id=user_id)
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        personnel_id=user.personnel_id,
        create_time=user.create_time,
        update_time=user.update_time
    )

@router.put("/{user_id}", response_model=UserResponse,summary="更新用户信息（仅管理员）")
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Any:
    """更新用户信息（仅管理员）"""
    user = user_service.update_user(db, user_id=user_id, user_in=user_in)
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        personnel_id=user.personnel_id,
        create_time=user.create_time,
        update_time=user.update_time
    )

@router.delete("/{user_id}", summary="删除用户（仅管理员）")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """删除用户（仅管理员）"""
    user_service.delete_user(db, user_id=user_id, current_user_id=int(current_user["id"]))
    return {"message": "用户删除成功"}

@router.post("/{user_id}/reset-password", summary="重置用户密码（仅管理员）")
def reset_user_password(
    user_id: int,
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """重置用户密码（仅管理员）"""
    user_service.reset_password(db, user_id=user_id, reset_data=reset_data)
    return {"message": "密码重置成功"}
