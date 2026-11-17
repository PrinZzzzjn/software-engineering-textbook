"""用户模块的业务规则：建号与登录（教材 6.4）。"""

from fastapi import HTTPException

from app.core.security import create_access_token, get_password_hash, verify_password
from app.modules.user import crud
from app.modules.user.model import User


def create_user(db, data) -> User:
    """注册：先查重，再哈希，最后入库。用户名重复返回 400。"""
    if crud.get_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=data.username,
        password_hash=get_password_hash(data.password),
    )
    return crud.create(db, user)


def login(db, data) -> dict:
    """登录：查用户 → 验密码 → 发令牌。

    两种失败都返回 401，且提示相同，避免泄露“用户名是否存在”。
    is_active 的检查在第 7 章启用/禁用时加入。
    """
    user = crud.get_by_username(db, data.username)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
