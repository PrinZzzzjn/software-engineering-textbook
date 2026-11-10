from typing import Any, Dict, Optional
from datetime import timedelta
from sqlalchemy.orm import Session
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.config.setting import settings
from app.core.exceptions import UnauthorizedException, BadRequestException
from app.api.v1.module_system.user.service import user_service
import redis
import json

class AuthService:
    """认证服务类"""
    
    def __init__(self):
        """初始化认证服务"""
        self.user_service = user_service
        # 初始化Redis客户端（用于存储令牌黑名单）
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            # 测试连接
            self.redis_client.ping()
            self.use_redis = True
        except:
            # Redis不可用时，使用内存存储（仅用于开发环境）
            self.token_blacklist = set()
            self.use_redis = False
    
    def login(self, db: Session, *, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        # 验证用户
        user = self.user_service.authenticate_user(db, username=username, password=password)
        if not user:
            raise UnauthorizedException(detail="用户名或密码错误")
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value if hasattr(user.role, 'value') else user.role},
            expires_delta=access_token_expires
        )
        
        # 创建刷新令牌
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        # 返回登录信息
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role.value if hasattr(user.role, 'value') else user.role
            }
        }
    
    def refresh_token(self, *, refresh_token: str) -> Dict[str, Any]:
        """刷新访问令牌"""
        # 检查令牌是否在黑名单中
        if self.is_token_blacklisted(refresh_token):
            raise UnauthorizedException(detail="无效的刷新令牌")
        
        # 解析令牌
        payload = decode_token(refresh_token)
        if not payload:
            raise UnauthorizedException(detail="无效的刷新令牌")
        
        # 验证是否为刷新令牌（通过检查是否包含角色信息）
        if "role" in payload:
            raise UnauthorizedException(detail="无效的刷新令牌")
        
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException(detail="无效的刷新令牌")
        
        # 创建新的访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id, "role": "user"},  # 注意：这里角色信息简化了，实际应该从数据库获取
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def logout(self, *, token: str) -> None:
        """用户登出，将令牌加入黑名单"""
        # 解析令牌获取过期时间
        payload = decode_token(token)
        if payload:
            # 计算剩余过期时间
            import time
            expires_at = payload.get("exp")
            if expires_at:
                remaining_time = max(0, expires_at - int(time.time()))
                # 将令牌加入黑名单
                self.blacklist_token(token, remaining_time)
    
    def get_current_user_info(self, db: Session, *, user_id: int) -> Dict[str, Any]:
        """获取当前用户信息"""
        return self.user_service.get_current_user_info(db, user_id=user_id)
    
    def change_password(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        old_password: str, 
        new_password: str, 
        confirm_password: str
    ) -> None:
        """修改用户密码"""
        # 验证新密码和确认密码是否一致
        if new_password != confirm_password:
            raise BadRequestException(detail="新密码与确认密码不一致")
        
        # 修改密码
        self.user_service.change_password(
            db, 
            user_id=user_id, 
            old_password=old_password, 
            new_password=new_password
        )
    
    def blacklist_token(self, token: str, expire_seconds: int) -> None:
        """将令牌加入黑名单"""
        if self.use_redis:
            # 使用Redis存储黑名单
            self.redis_client.setex(
                f"blacklist:{token}",
                expire_seconds,
                "1"
            )
        else:
            # 使用内存存储（仅用于开发环境）
            self.token_blacklist.add(token)
    
    def is_token_blacklisted(self, token: str) -> bool:
        """检查令牌是否在黑名单中"""
        if self.use_redis:
            # 使用Redis检查
            return self.redis_client.exists(f"blacklist:{token}") > 0
        else:
            # 使用内存检查
            return token in self.token_blacklist

# 创建认证服务实例
auth_service = AuthService()
