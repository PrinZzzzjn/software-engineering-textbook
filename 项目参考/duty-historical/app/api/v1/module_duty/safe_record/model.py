from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
import enum
from app.core.base_model import BaseModel
from app.api.v1.module_duty.dept.model import Department
from app.api.v1.module_duty.personnel.model import Personnel

class ApplicationType(str, enum.Enum):
    """申请类型枚举"""
    WORKSTATION = "01"  # 工位申请
    DUTY_ROOM = "02"     # 值班室供应
    LINKAGE = "03"       # 联动申请
    SAFE_CONTROLLER = "04"  # 保险箱控制器
    KEY_OPEN = "05"      # 钥匙开启

class AuthorizationType(str, enum.Enum):
    """授权类型枚举"""
    DUTY_ROOM = "01"     # 值班室授权
    LINKAGE = "02"       # 联动授权
    SAFE_CONTROLLER = "03"  # 保险箱控制器
    SAFE_KEY = "04"      # 保险箱钥匙
    ON_SITE = "05"       # 实地供应

class AuthorizationResult(str, enum.Enum):
    """授权结果枚举"""
    SUCCESS = "01"       # 成功
    FAILURE = "02"       # 失败
    TIMEOUT = "03"       # 超时
    REJECT = "04"        # 拒绝

class SafeBoxRecord(BaseModel):
    """保险箱开关记录模型"""
    __tablename__ = "safe_box_records"
    
    dept_code = Column(String(50), ForeignKey("dept.dept_code"), nullable=False, comment='部门编码')
    device_id = Column(String(100), nullable=False, comment='设备ID')
    applicant_certificate_number = Column(String(50), ForeignKey("personnel.certificate_number"), nullable=False, comment='申请人证书编号')
    application_time = Column(DateTime(timezone=True), nullable=False, comment='申请时间')
    application_type = Column(SQLEnum(ApplicationType), nullable=False, comment='申请类型内码')
    authorizer_certificate_number = Column(String(50), ForeignKey("personnel.certificate_number"), nullable=False, comment='授权人证书编号')
    authorization_type = Column(SQLEnum(AuthorizationType), nullable=False, comment='授权类型内码')
    authorization_result = Column(SQLEnum(AuthorizationResult), nullable=False, comment='授权结果内码')
    open_time = Column(DateTime(timezone=True), nullable=True, comment='保险箱开启时间')
    close_time = Column(DateTime(timezone=True), nullable=True, comment='保险箱关闭时间')
    is_test_mode = Column(Boolean, default=False, comment='是否测试模式(0:否,1:是)')
    
    # 索引
    __table_args__ = (
        Index('idx_safe_box_dept', 'dept_code'),
        Index('idx_safe_box_device', 'device_id'),
        Index('idx_safe_box_applicant', 'applicant_certificate_number'),
        Index('idx_safe_box_application_time', 'application_time'),
    )
    
    # 关系定义
    department = relationship("Department", foreign_keys=[dept_code], back_populates="safe_box_records")
    applicant = relationship("Personnel", foreign_keys=[applicant_certificate_number], back_populates="safe_box_applications")
    authorizer = relationship("Personnel", foreign_keys=[authorizer_certificate_number], back_populates="safe_box_authorizations")
