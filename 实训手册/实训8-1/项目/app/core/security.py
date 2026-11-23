"""密码哈希、令牌登记与校验、当前用户依赖。

对应教材 8.2 与 8.4，文件按“哈希 → 令牌 → 依赖”排列。
第 9 章会在这里追加管理员依赖。
"""

import hashlib
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db


ITERATIONS = 100_000


def get_password_hash(password: str) -> str:
    """注册时调用：生成随机盐，用 PBKDF2 迭代 100000 次，返回“盐$迭代次数$摘要”。"""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), ITERATIONS
    ).hex()
    return f"{salt}${ITERATIONS}${digest}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """登录时调用：从存储值取出盐与迭代次数，用同样的参数重算摘要并比对。"""
    salt, iterations, digest = hashed_password.split("$", 2)
    candidate = hashlib.pbkdf2_hmac(
        "sha256", plain_password.encode(), bytes.fromhex(salt), int(iterations)
    ).hex()
    return secrets.compare_digest(candidate, digest)


# 令牌表：token -> user_id，内存字典，重启即清空
TOKEN_STORE: dict[str, int] = {}


def create_access_token(user_id: int) -> str:
    """登录成功后签发：生成随机令牌，登记它属于哪个用户。"""
    token = secrets.token_hex(16)
    TOKEN_STORE[token] = user_id
    return token


def resolve_token(token: str) -> int | None:
    """校验令牌：查字典得到 user_id，查不到返回 None。"""
    return TOKEN_STORE.get(token)


# auto_error=False：没带令牌时不在这里抛错，交由 get_current_user 统一返回 401。
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """受保护接口的依赖：取出令牌、查字典、再查 users 表取角色。

    未带令牌、令牌未登记、按 user_id 查不到用户，均返回 401。
    """
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
