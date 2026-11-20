from sqlalchemy import Column, Integer, String, Enum as SQLEnum
import enum
from app.core.base_model import BaseModel

class UserRole(enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"      # 管理员
    NORMAL = "normal"    # 普通用户

class User(BaseModel):
    """系统用户模型（服务认证和授权）"""
    __tablename__ = "users"
    
    username = Column(String(100), unique=True, nullable=False, index=True, comment='用户名')
    password_hash = Column(String(255), nullable=False, comment='密码哈希')
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.NORMAL, comment='用户角色')
    is_active = Column(Integer, default=1, comment='账号状态(0:禁用,1:启用)')
    personnel_id = Column(Integer, nullable=True, comment='关联的人员ID（可选，用于系统用户与实际人员的关联）')
