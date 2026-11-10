from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import relationship
import enum
from app.core.base_model import BaseModel
from app.api.v1.module_duty.dept.model import Department
from app.api.v1.module_duty.personnel.model import Personnel

class OpenReasonType(enum.Enum):
    """开启原因枚举"""
    TYPE_01 = "01"
    TYPE_02 = "02"
    TYPE_03 = "03"

class CabinetOpenType(enum.Enum):
    """开柜类型枚举"""
    DUTY_ROOM = "01"     # 值班室开启
    KEY_OPEN = "02"      # 钥匙开启
    TERMINAL_CONTROL = "03"  # 终端控制开启

class CabinetOpenResult(enum.Enum):
    """开柜结果枚举"""
    NORMAL = "01"        # 正常
    REJECT = "02"        # 拒绝
    KEY_OPEN = "03"        # 钥匙开柜

class EquipmentCabinetRecord(BaseModel):
    """设备柜开关记录模型"""
    __tablename__ = "equipment_cabinet_records"
    
    dept_code = Column(String(50), ForeignKey("dept.dept_code"), nullable=False, comment='部门编码')
    device_id = Column(String(100), nullable=False, comment='设备ID')
    open_reason_type = Column(SQLEnum(OpenReasonType), nullable=False, comment='开启原因内码')
    applicant_certificate_number = Column(String(50), ForeignKey("personnel.certificate_number"), nullable=False, comment='申请人证书编号')
    application_time = Column(DateTime(timezone=True), nullable=False, comment='申请时间')
    cabinet_open_time = Column(DateTime(timezone=True), nullable=True, comment='设备柜开启时间')
    cabinet_close_time = Column(DateTime(timezone=True), nullable=True, comment='设备柜关闭时间')
    authorizer_certificate_number = Column(String(50), ForeignKey("personnel.certificate_number"), nullable=False, comment='授权人证书编号')
    open_type = Column(SQLEnum(CabinetOpenType), nullable=False, comment='开柜类型内码')
    open_result = Column(SQLEnum(CabinetOpenResult), nullable=False, comment='开柜结果内码')
    device_quantity_change = Column(String(50), comment='设备数量变化(示例：1->2)')
    
    # 索引
    __table_args__ = (
        Index('idx_cabinet_dept', 'dept_code'),
        Index('idx_cabinet_device', 'device_id'),
        Index('idx_cabinet_applicant', 'applicant_certificate_number'),
        Index('idx_cabinet_application_time', 'application_time'),
    )
    
    # 关系定义
    department = relationship("Department", foreign_keys=[dept_code], back_populates="equipment_cabinet_records")
    applicant = relationship("Personnel", foreign_keys=[applicant_certificate_number], back_populates="cabinet_applications")
    authorizer = relationship("Personnel", foreign_keys=[authorizer_certificate_number], back_populates="cabinet_authorizations")
