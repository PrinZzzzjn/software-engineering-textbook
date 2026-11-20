from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.api.v1.module_system.user.model import User, UserRole
from app.api.v1.module_system.user.schema import UserCreate, UserUpdate
from app.api.v1.module_system.user.param import UserQueryParams
from app.core.base_crud import BaseCRUD
from app.core.security import get_password_hash

class UserCRUD(BaseCRUD[User, UserCreate, UserUpdate]):
    """用户CRUD操作类"""
    
    def __init__(self):
        """初始化用户CRUD类"""
        super().__init__(User)
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()
    
    def get_by_personnel_id(self, db: Session, *, personnel_id: int) -> Optional[User]:
        """根据人员ID获取用户"""
        return db.query(User).filter(User.personnel_id == personnel_id).first()
    
    def get_multi_by_role(self, db: Session, *, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """根据角色获取多个用户"""
        return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()
    
    def get_active_users(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """获取活跃用户列表"""
        return db.query(User).filter(User.is_active == 1).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """创建用户，自动哈希密码"""
        # 转换为字典并处理密码哈希
        db_obj = User(
            username=obj_in.username,
            password_hash=get_password_hash(obj_in.password),
            role=obj_in.role,
            is_active=obj_in.is_active,
            personnel_id=obj_in.personnel_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_password(self, db: Session, *, db_obj: User, password: str) -> User:
        """更新用户密码"""
        db_obj.password_hash = get_password_hash(password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_paginated(self, db: Session, *, params: UserQueryParams) -> Dict[str, Any]:
        """根据查询参数分页获取用户列表"""
        # 构建查询
        query = db.query(User)
        
        # 应用过滤条件
        if params.username:
            query = query.filter(User.username.ilike(f"%{params.username}%"))
        
        if params.role is not None:
            query = query.filter(User.role == params.role)
        
        if params.is_active is not None:
            query = query.filter(User.is_active == params.is_active)
        
        if params.personnel_id is not None:
            query = query.filter(User.personnel_id == params.personnel_id)
        
        # 应用搜索关键词
        if params.keyword:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{params.keyword}%"),
                    User.role == params.keyword
                )
            )
        
        # 应用排序
        if params.sort_by and params.sort_order:
            order_column = getattr(User, params.sort_by, User.id)
            if params.sort_order.lower() == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        else:
            query = query.order_by(User.id.desc())
        
        # 使用父类的分页方法
        return super().get_paginated(
            db, 
            page=params.page, 
            page_size=params.page_size, 
            query=query
        )
    
    def exists_by_username(self, db: Session, *, username: str, exclude_id: Optional[int] = None) -> bool:
        """检查用户名是否已存在"""
        query = db.query(User).filter(User.username == username)
        if exclude_id is not None:
            query = query.filter(User.id != exclude_id)
        return query.first() is not None

# 创建用户CRUD实例
user_crud = UserCRUD()
