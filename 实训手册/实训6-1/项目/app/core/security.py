"""密码哈希、令牌签发与解析、当前用户依赖。

对应教材 6.3 与 6.5，文件按“哈希 → 令牌 → 依赖”排列。
第 7 章会在这里追加管理员依赖。
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# 读取 .env（第 5 章 5.6 创建）；未设置时使用教学占位值，正式部署必须设置 SECRET_KEY。
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-env")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 哈希方案固定为 pbkdf2_sha256：注册与登录必须用同一个对象，否则校验必然失败。
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# auto_error=False：没带令牌时不在这里抛错，交由 get_current_user 统一返回 401。
bearer_scheme = HTTPBearer(auto_error=False)


def get_password_hash(password: str) -> str:
    """注册时调用：把明文密码变成不可逆的哈希值。"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """登录时调用：用同一方案校验输入与库中的哈希是否一致。"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """登录成功后签发令牌：在载荷上加过期时间，再用 SECRET_KEY 签名。"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """解析并校验令牌；签名不对或已过期时返回 None，由调用方转成 401。"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """受保护接口的依赖：从 Authorization: Bearer <token> 取出并验证令牌。

    未带令牌、令牌无效或过期，均返回 401；通过后把当前用户交给接口。
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="未提供令牌")
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("sub") is None:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    # sub 在 JWT 中是字符串，转回整数，后续比较 id 才不会类型不符。
    return {"id": int(payload["sub"]), "role": payload.get("role")}
