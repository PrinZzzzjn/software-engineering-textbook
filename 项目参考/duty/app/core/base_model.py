from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from .database import Base

class BaseModel(Base):
    """所有模型的基础类，提供通用字段和功能"""
    __abstract__ = True
    
    # 主键字段
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    
    # 时间戳字段，自动生成
    create_time = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        """提供模型的字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>"