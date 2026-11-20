from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import relationship
from app.core.base_model import BaseModel

class DutyRecord(BaseModel):
    """值班记录模型"""
    __tablename__ = "duty_records"
    
    personnel_certificate_number = Column(String(50), ForeignKey("personnel.certificate_number"), nullable=False, comment='值班人员证件号')
    successor_certificate_number = Column(String(50), ForeignKey("personnel.certificate_number"), comment='接班人员证件号')
    start_time = Column(DateTime(timezone=True), nullable=False, comment='值班开始时间')
    end_time = Column(DateTime(timezone=True), nullable=False, comment='值班结束时间')
    workstation_id = Column(String(50), ForeignKey("workstations.workstation_id"), comment='值班工位id')
    status = Column(String(20), default='normal', comment='值班状态')
    remark = Column(String(500), comment='备注')
    created_by = Column(String(50), comment='创建人')
    
    # 索引
    __table_args__ = (
        Index('idx_personnel_time', 'personnel_certificate_number', 'start_time'),
        Index('idx_workstation_time', 'workstation_id', 'start_time'),
    )
    
    # 关系定义
    personnel = relationship("Personnel", back_populates="duty_records", foreign_keys=[personnel_certificate_number])
    successor = relationship("Personnel", foreign_keys=[successor_certificate_number])
    workstation = relationship("Workstation", back_populates="duty_records")
    inspection_records = relationship("InspectionRecord", back_populates="duty_record", cascade="all, delete-orphan")
