"""用户模块的输入与输出模型：管什么能进、什么能出（教材 6.4）。"""

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """注册的输入模型：只收用户名与密码；role 不由客户端决定。"""

    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=50)


class UserOut(BaseModel):
    """注册与用户信息的输出模型：不含 password_hash。"""

    id: int
    username: str
    role: str
    is_active: int


class LoginIn(BaseModel):
    """登录的输入模型：只校验“有没有传”，密码是否正确由 service 判断。"""

    username: str
    password: str


class TokenOut(BaseModel):
    """登录成功的输出模型：令牌与类型，前端据此拼请求头。"""

    access_token: str
    token_type: str = "bearer"
