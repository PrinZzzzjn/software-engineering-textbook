import hashlib
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db


ITERATIONS = 100_000


def get_password_hash(password: str) -> str:
    """用随机盐 + PBKDF2 把密码哈希化，返回 "盐$迭代次数$摘要"。"""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), ITERATIONS
    ).hex()
    return f"{salt}${ITERATIONS}${digest}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码是否与已存储的哈希匹配。"""
    salt, iterations, digest = hashed_password.split("$", 2)
    candidate = hashlib.pbkdf2_hmac(
        "sha256", plain_password.encode("utf-8"), bytes.fromhex(salt), int(iterations)
    ).hex()
    return secrets.compare_digest(candidate, digest)


# 令牌表：token -> user_id，内存字典，重启即失（与用户表一致）
TOKEN_STORE: dict[str, int] = {}


def create_access_token(user_id: int) -> str:
    token = secrets.token_hex(16)
    TOKEN_STORE[token] = user_id
    return token


def resolve_token(token: str) -> int | None:
    return TOKEN_STORE.get(token)


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="未提供令牌")
    user_id = resolve_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="令牌无效")
    from app.modules.user import crud
    user = crud.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="令牌无效")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="账号已禁用")
    return {"id": user.id, "role": user.role}


def get_current_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    return current_user
