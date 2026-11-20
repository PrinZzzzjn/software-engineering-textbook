from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base_model import BaseModel

class Personnel(BaseModel):
    """人员信息模型"""
    __tablename__ = "personnel"
    
    name = Column(String(100), nullable=False, comment='姓名')
    certificate_number = Column(String(50), unique=True, nullable=False, comment='证件号')
    id_card_number = Column(String(20), unique=True, nullable=False, comment='身份证号')
    dept_code = Column(String(50), ForeignKey("dept.dept_code"), comment='部门编码')
    position = Column(String(100), comment='职务')
    rank = Column(String(50), comment='职级')
    hire_date = Column(Date, comment='入职日期')
    
    # 关系定义
    department = relationship("Department", back_populates="personnel", foreign_keys=[dept_code])
    # 启用已开发模型的关联关系，明确指定外键
    duty_records = relationship("DutyRecord", back_populates="personnel", foreign_keys="DutyRecord.personnel_certificate_number", cascade="all, delete-orphan")
    # 启用与查班记录的关联关系
    inspection_records = relationship("InspectionRecord", back_populates="inspector", foreign_keys="InspectionRecord.inspector_certificate_number")
    safe_box_applications = relationship("SafeBoxRecord", back_populates="applicant", foreign_keys="SafeBoxRecord.applicant_certificate_number", cascade="all, delete-orphan")
    safe_box_authorizations = relationship("SafeBoxRecord", back_populates="authorizer", foreign_keys="SafeBoxRecord.authorizer_certificate_number", cascade="all, delete-orphan")
    cabinet_applications = relationship("EquipmentCabinetRecord", back_populates="applicant", foreign_keys="EquipmentCabinetRecord.applicant_certificate_number", cascade="all, delete-orphan")
    cabinet_authorizations = relationship("EquipmentCabinetRecord", back_populates="authorizer", foreign_keys="EquipmentCabinetRecord.authorizer_certificate_number", cascade="all, delete-orphan")
    # processed_inspection_events = relationship("InspectionEvent", back_populates="processor", cascade="all, delete-orphan")
