from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.base_schema import BaseSchema

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
    user: Dict[str, Any] = Field(..., description="用户信息")

# 当前用户信息响应模型
class CurrentUserResponse(BaseSchema):
    """当前用户信息"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="用户角色")
    created_at: datetime = Field(..., description="创建时间")

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
