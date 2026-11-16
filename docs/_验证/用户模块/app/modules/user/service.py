from fastapi import HTTPException

from app.core.security import create_access_token, get_password_hash, verify_password
from app.modules.user.model import User


def create_user(db, data) -> User:
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=data.username,
        password_hash=get_password_hash(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(db, data) -> dict:
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="账号已禁用")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


def list_users(db) -> dict:
    users = db.query(User).order_by(User.id).limit(50).all()
    return {
        "items": [
            {"id": u.id, "username": u.username, "role": u.role, "is_active": u.is_active}
            for u in users
        ],
        "count": len(users),
    }


def update_user(db, user_id: int, data, current_user: dict) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if current_user["id"] == user_id and data.is_active == 0:
        raise HTTPException(status_code=400, detail="不能禁用自己")
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    db.commit()
    db.refresh(user)
    return user
