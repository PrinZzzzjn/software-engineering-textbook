from fastapi import HTTPException

from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.modules.user import crud
from app.modules.user.model import User


def create_user(db, data) -> User:
    if crud.get_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    return crud.create(db, data.username, get_password_hash(data.password))


def list_users(db, params) -> dict:
    """用户列表：复用第 7 章定型的分页骨架，返回本页数据与总数。"""
    offset = (params.page - 1) * params.page_size
    items, total = crud.list_page(db, offset, params.page_size)
    return {
        "items": [
            {
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "is_active": u.is_active,
            }
            for u in items
        ],
        "total": total,
    }


def update_user(db, user_id: int, data, current_user: dict) -> User:
    user = crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if current_user["id"] == user_id and data.is_active == 0:
        raise HTTPException(status_code=400, detail="不能禁用自己")
    return crud.update(db, user, data.model_dump(exclude_unset=True))


def authenticate(db, data) -> tuple[str, User]:
    """核对用户名与密码，返回一个简单令牌和对应的用户对象。

    令牌登记进 TOKEN_STORE（token -> user_id），重启即失效；
    用户角色不写进令牌，每次由 get_current_user 查用户表取得。
    """
    user = crud.get_by_username(db, data.username)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已停用")
    return create_access_token(user.id), user
