from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user, oauth2_scheme
from app.api.v1.module_system.auth.schema import (
    LoginRequest, LoginResponse, RefreshTokenRequest, TokenResponse,
    CurrentUserResponse, ChangePasswordRequest
)
from app.api.v1.module_system.auth.service import auth_service

router = APIRouter()

@router.post("/login", response_model=LoginResponse,summary="用户登录")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """用户登录"""
    result = auth_service.login(
        db, 
        username=login_data.username, 
        password=login_data.password
    )
    return LoginResponse(**result)

@router.post("/login/form", response_model=LoginResponse,summary="OAuth2兼容的登录接口")
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """OAuth2兼容的登录接口"""
    result = auth_service.login(
        db, 
        username=form_data.username, 
        password=form_data.password
    )
    return LoginResponse(**result)

@router.post("/refresh", response_model=TokenResponse,summary="刷新令牌")
def refresh(
    refresh_data: RefreshTokenRequest
) -> Any:
    """刷新令牌"""
    result = auth_service.refresh_token(
        refresh_token=refresh_data.refresh_token
    )
    return TokenResponse(**result)

@router.post("/logout", summary="用户登出")
def logout(
    token: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """用户登出"""
    auth_service.logout(token=token)
    return {"message": "登出成功"}

@router.get("/me", response_model=CurrentUserResponse,summary="获取当前用户信息")
def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取当前用户信息"""
    user_info = auth_service.get_current_user_info(
        db, 
        user_id=int(current_user["id"])
    )
    return CurrentUserResponse(**user_info)

@router.post("/change-password", summary="修改密码")
def change_password(
    change_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """修改密码"""
    auth_service.change_password(
        db,
        user_id=int(current_user["id"]),
        old_password=change_data.old_password,
        new_password=change_data.new_password,
        confirm_password=change_data.confirm_password
    )
    return {"message": "密码修改成功"}
