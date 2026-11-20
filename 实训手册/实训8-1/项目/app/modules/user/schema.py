"""用户模块的输入与输出模型：管什么能进、什么能出（教材 6.3）。"""

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """注册的输入模型：只收用户名与密码；role 不由客户端决定。"""

    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class UserOut(BaseModel):
    """注册与用户信息的输出模型：不含 password_hash。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    is_active: int


class UserLogin(BaseModel):
    """登录的输入模型：只校验“有没有传”，密码是否正确由 service 判断。"""

    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=128)


class TokenOut(BaseModel):
    """登录成功的输出模型：令牌、类型与当前用户公开信息。"""

    access_token: str
    token_type: str = "bearer"
    user: UserOut
