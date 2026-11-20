from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.config.setting import settings
from .database import SessionLocal
from .security import has_permission

# OAuth2密码承载令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/form")

# 获取数据库会话的依赖
def get_db() -> Generator:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 获取当前用户信息的依赖
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """获取当前认证用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 这里应该从数据库获取用户信息
    # 为了演示，直接返回payload中的信息
    return {"id": user_id, "role": user_role}

# 通用权限检查依赖
def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """获取当前活跃用户"""
    # 实际应用中可能需要检查用户状态
    return current_user

# 管理员权限检查依赖
def get_current_admin_user(current_user: dict = Depends(get_current_active_user)):
    """获取具有管理员权限的用户"""
    if not has_permission(current_user["role"], "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# 普通用户权限检查依赖
def get_current_normal_user(current_user: dict = Depends(get_current_active_user)):
    """获取普通用户（包括管理员）"""
    # 所有认证用户都可以作为普通用户访问
    return current_user