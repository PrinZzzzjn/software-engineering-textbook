from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base_model import BaseModel

class Department(BaseModel):
    """部门模型"""
    __tablename__ = "dept"
    
    # 单位内码（保持与数据库定义一致）
    dept_code = Column(String(50), nullable=False, unique=True, comment="单位内码")
    # 单位全称
    full_name = Column(String(255), nullable=False, comment="单位全称")
    # 单位地址
    address = Column(String(500), nullable=True, comment="单位地址")
    # 经度
    longitude = Column(Float, nullable=True, comment="经度")
    # 纬度
    latitude = Column(Float, nullable=True, comment="纬度")
    # 上级部门
    parent_dept_code = Column(String(50), ForeignKey("dept.dept_code"), nullable=True, comment="上级部门编码")
    
    # 关联关系
    # 添加primaryjoin明确指定自引用关系的连接条件
    parent_dept = relationship("Department", remote_side=[dept_code], backref="child_depts", 
                             primaryjoin="Department.parent_dept_code==Department.dept_code")
    safe_box_records = relationship("SafeBoxRecord", back_populates="department", cascade="all, delete-orphan")
    equipment_cabinet_records = relationship("EquipmentCabinetRecord", back_populates="department", cascade="all, delete-orphan")
    # 关系定义：一个部门可以有多个工位
    workstations = relationship("Workstation", back_populates="department", cascade="all, delete-orphan")
    # 关系定义：一个部门可以有多个人员
    personnel = relationship("Personnel", back_populates="department", cascade="all, delete-orphan")
