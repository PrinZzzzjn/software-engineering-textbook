from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config.setting import settings

# 密码加密上下文
# 使用pbkdf2_sha256替代bcrypt，解决密码长度限制问题
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto", pbkdf2_sha256__rounds=100000)

# 密码哈希函数
def get_password_hash(password: str) -> str:
    """获取密码的哈希值"""
    return pwd_context.hash(password)

# 密码验证函数
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否正确"""
    return pwd_context.verify(plain_password, hashed_password)

# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 创建刷新令牌
def create_refresh_token(data: dict) -> str:
    """创建JWT刷新令牌"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 解析令牌
def decode_token(token: str) -> Union[dict, None]:
    """解析JWT令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

# 权限检查函数
def has_permission(user_role: str, required_role: str) -> bool:
    """
    检查用户角色是否具有所需权限（不区分大小写）
    简单实现：假设admin角色具有所有权限
    """
    if not user_role:
        return False
    # 转换为小写进行比较，避免大小写问题
    user_role_lower = user_role.lower()
    required_role_lower = required_role.lower()
    
    if user_role_lower == "admin":
        return True
    return user_role_lower == required_role_lower