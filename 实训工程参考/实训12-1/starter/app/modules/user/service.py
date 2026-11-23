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
    if not user.is_active:
        raise HTTPException(status_code=401, detail="账号已禁用")
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer", "user": user}


def list_users(db, params) -> dict:
    """用户列表：复用第 7 章定型的分页骨架，返回本页数据与总数。"""
    offset = (params.page - 1) * params.page_size
    items, total = crud.list_page(db, offset, params.page_size)
    return {"items": items, "total": total}


def update_user(db, user_id: int, data, current_user: dict) -> User:
    """修改角色与启用状态：先查存在性（404），再查业务规则（400），最后写入。"""
    user = crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if current_user["id"] == user_id and data.is_active == 0:
        raise HTTPException(status_code=400, detail="不能禁用自己")
    return crud.update(db, user, data.model_dump(exclude_unset=True))


def create_admin(db, username: str = "admin", password: str = "admin123") -> User:
    """幂等创建管理员账号，供启动 seed 与后续章节使用。"""
    user = crud.get_by_username(db, username)
    if user:
        return user
    user = crud.create(db, username, get_password_hash(password))
    return crud.update(db, user, {"role": "admin"})
