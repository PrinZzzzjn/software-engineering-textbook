from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.api.v1.module_system.user.model import UserRole
from app.core.base_schema import BaseSchema

# 用户基础信息模型
class UserBase(BaseSchema):
    """用户基础信息"""
    username: str = Field(..., min_length=3, max_length=100, description="用户名")
    role: UserRole = Field(default=UserRole.NORMAL, description="用户角色")
    is_active: int = Field(default=1, ge=0, le=1, description="账号状态(0:禁用,1:启用)")
    personnel_id: Optional[int] = Field(default=None, description="关联的人员ID")

# 用户创建请求模型
class UserCreate(UserBase):
    """用户创建请求"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")

# 用户更新请求模型
class UserUpdate(BaseSchema):
    """用户更新请求"""
    role: Optional[UserRole] = Field(default=None, description="用户角色")
    is_active: Optional[int] = Field(default=None, ge=0, le=1, description="账号状态(0:禁用,1:启用)")
    personnel_id: Optional[int] = Field(default=None, description="关联的人员ID")

# 用户响应模型
class UserResponse(UserBase):
    """用户信息响应"""
    id: int = Field(..., description="用户ID")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

# 用户列表响应项模型
class UserListItem(BaseSchema):
    """用户列表项"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: UserRole = Field(..., description="用户角色")
    is_active: int = Field(..., description="账号状态")
    personnel_id: Optional[int] = Field(default=None, description="关联的人员ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

# 重置密码请求模型
class ResetPasswordRequest(BaseSchema):
    """重置密码请求"""
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")

# 修改密码请求模型
class ChangePasswordRequest(BaseSchema):
    """修改密码请求"""
    old_password: str = Field(..., min_length=6, max_length=50, description="原密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")
    confirm_password: str = Field(..., min_length=6, max_length=50, description="确认密码")
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, info):
        """验证新密码和确认密码是否一致"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('新密码与确认密码不一致')
        return v

# 登录请求模型
class LoginRequest(BaseSchema):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

# 刷新令牌请求模型
class RefreshTokenRequest(BaseSchema):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌")

# 令牌响应模型
class TokenResponse(BaseSchema):
    """令牌响应"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: Optional[str] = Field(default=None, description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(default=1800, description="过期时间（秒）")

# 登录响应模型
class LoginResponse(TokenResponse):
    """登录响应"""
    user: dict = Field(..., description="用户信息")

# 当前用户信息响应模型
class CurrentUserResponse(BaseSchema):
    """当前用户信息"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: UserRole = Field(..., description="用户角色")
    created_at: datetime = Field(..., description="创建时间")
