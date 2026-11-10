from sqlalchemy import Column, String, Integer, Float, Index, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base_model import BaseModel


class Workstation(BaseModel):
    """工位信息模型"""
    __tablename__ = "workstations"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    workstation_id = Column(String(50), nullable=False, unique=True, index=True, comment='工位id')
    workstation_name = Column(String(100), nullable=False, index=True, comment='工位名称')
    dept_code = Column(String(50), ForeignKey('dept.dept_code'), nullable=False, comment='单位内码')
    category_code = Column(String(50), nullable=True, index=True, comment='工位类别内码')
    longitude = Column(Float, comment='经度')
    latitude = Column(Float, comment='纬度')
    remark = Column(String(500), comment='备注')
    
    # 索引
    __table_args__ = (
        Index('idx_workstation_id', 'workstation_id', unique=True),
        Index('idx_workstation_name', 'workstation_name'),
        Index('idx_category_code', 'category_code'),
        Index('idx_dept_code', 'dept_code'),
    )
    
    # 关系定义
    duty_records = relationship("DutyRecord", back_populates="workstation", cascade="all, delete-orphan")
    # 关系定义：一个工位属于一个部门，一个部门可以有多个工位
    department = relationship("Department", back_populates="workstations")
