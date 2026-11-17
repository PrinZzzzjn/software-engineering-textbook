"""用户表模型：定义 users 表存哪些列、各列受什么约束（教材 6.2）。"""

from sqlalchemy import Column, Integer, String

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)  # 主键，同时写进令牌的 sub
    username = Column(String(100), unique=True, nullable=False)  # 唯一且必填
    password_hash = Column(String(255), nullable=False)  # 只存哈希，不存明文
    role = Column(String(20), default="normal")  # 第 7 章据此判断权限
    is_active = Column(Integer, default=1)  # 第 7 章用于启用与禁用
