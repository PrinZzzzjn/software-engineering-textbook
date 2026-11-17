"""用户模块的接口层：注册、登录、当前用户（教材 6.4–6.5）。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.user import service
from app.modules.user.schema import LoginIn, TokenOut, UserCreate, UserOut

# 模块级路由：前缀只写本资源名，"/api/v1" 由根目录 main.py 提供。
router = APIRouter(prefix="/users", tags=["用户"])


@router.post("", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """注册：201；重名由 service 返回 400；字段不合法由模型在进入函数前返回 422。"""
    return service.create_user(db, data)


@router.post("/login", response_model=TokenOut)
def login_endpoint(data: LoginIn, db: Session = Depends(get_db)):
    """登录：200 + 令牌；用户名或密码错误返回 401。"""
    return service.login(db, data)


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    """当前用户：依赖通过后返回 {id, role}；未带或无效令牌返回 401。"""
    return current_user
