from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.api.v1.module_system.user.model import User
from app.api.v1.module_system.user.schema import UserCreate, UserUpdate, ResetPasswordRequest
from app.api.v1.module_system.user.param import UserQueryParams
from app.api.v1.module_system.user.crud import user_crud
from app.core.exceptions import NotFoundException, BadRequestException, DuplicateResourceException
from app.core.security import verify_password, get_password_hash

class UserService:
    """用户管理服务类"""
    
    def __init__(self):
        """初始化用户服务"""
        self.crud = user_crud
    
    def get_user_by_id(self, db: Session, *, user_id: int) -> User:
        """根据ID获取用户"""
        user = self.crud.get(db, id=user_id)
        if not user:
            raise NotFoundException(detail="用户不存在")
        return user
    
    def get_user_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.crud.get_by_username(db, username=username)
    
    def create_user(self, db: Session, *, user_in: UserCreate) -> User:
        """创建新用户"""
        # 检查用户名是否已存在
        if self.crud.exists_by_username(db, username=user_in.username):
            raise DuplicateResourceException(detail="用户名已存在")
        
        # 创建用户
        return self.crud.create(db, obj_in=user_in)
    
    def update_user(self, db: Session, *, user_id: int, user_in: UserUpdate) -> User:
        """更新用户信息"""
        # 获取用户
        user = self.get_user_by_id(db, user_id=user_id)
        
        # 更新用户信息
        update_data = user_in.model_dump(exclude_unset=True)
        return self.crud.update(db, db_obj=user, obj_in=update_data)
    
    def delete_user(self, db: Session, *, user_id: int, current_user_id: int) -> None:
        """删除用户"""
        # 不能删除当前登录用户
        if user_id == current_user_id:
            raise BadRequestException(detail="不能删除当前登录用户")
        
        # 获取用户
        user = self.get_user_by_id(db, user_id=user_id)
        
        # 删除用户
        self.crud.delete(db, id=user_id)
    
    def reset_password(self, db: Session, *, user_id: int, reset_data: ResetPasswordRequest) -> None:
        """重置用户密码"""
        # 获取用户
        user = self.get_user_by_id(db, user_id=user_id)
        
        # 更新密码
        self.crud.update_password(db, db_obj=user, password=reset_data.new_password)
    
    def get_user_list(self, db: Session, *, params: UserQueryParams) -> Dict[str, Any]:
        """获取用户列表"""
        return self.crud.get_paginated(db, params=params)
    
    def authenticate_user(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """认证用户"""
        # 获取用户
        user = self.get_user_by_username(db, username=username)
        if not user:
            return None
        
        # 验证用户状态
        if user.is_active != 1:
            return None
        
        # 验证密码
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    def change_password(self, db: Session, *, user_id: int, old_password: str, new_password: str) -> None:
        """修改用户密码"""
        # 获取用户
        user = self.get_user_by_id(db, user_id=user_id)
        
        # 验证原密码
        if not verify_password(old_password, user.password_hash):
            raise BadRequestException(detail="原密码错误")
        
        # 更新密码
        self.crud.update_password(db, db_obj=user, password=new_password)
    
    def get_current_user_info(self, db: Session, *, user_id: int) -> Dict[str, Any]:
        """获取当前用户信息"""
        user = self.get_user_by_id(db, user_id=user_id)
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "created_at": user.create_time
        }

# 创建用户服务实例
user_service = UserService()
