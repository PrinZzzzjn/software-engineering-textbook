from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    is_active: int


class UserPage(BaseModel):
    items: list[UserOut]
    total: int


class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=128)


class TokenOut(BaseModel):
    """登录成功后的响应：令牌 + 当前用户。令牌用于后续请求的 Bearer 头。"""

    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserUpdate(BaseModel):
    """修改用户时只允许改角色与启用状态；Literal 把允许值写进类型。"""

    role: Literal["admin", "normal"] | None = None
    is_active: Literal[0, 1] | None = None
