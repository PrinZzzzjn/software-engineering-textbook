from fastapi import HTTPException

from app.core.security import create_access_token, get_password_hash, verify_password
from app.modules.user import crud
from app.modules.user.model import User


def create_user(db, data) -> User:
    if crud.get_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    return crud.create(db, data.username, get_password_hash(data.password))


def login(db, data) -> dict:
    user = crud.get_by_username(db, data.username)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer", "user": user}


def create_admin(db, username: str = "admin", password: str = "admin123") -> User:
    """幂等创建管理员账号，供启动 seed 与后续章节使用。"""
    user = crud.get_by_username(db, username)
    if user:
        return user
    user = crud.create(db, username, get_password_hash(password))
    return crud.update(db, user, {"role": "admin"})
