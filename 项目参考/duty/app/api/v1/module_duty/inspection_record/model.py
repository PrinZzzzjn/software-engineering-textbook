from sqlalchemy import Column, Integer, DateTime, String, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import relationship
import enum
from app.core.base_model import BaseModel

class InspectionType(enum.Enum):
    """查班类型枚举"""
    ONLINE = "网络"
    ON_SITE = "实地"

class EvaluationLevel(enum.Enum):
    """评价等级枚举"""
    GOOD = "好"
    MEDIUM = "中"
    POOR = "差"

class InspectionRecord(BaseModel):
    """查班记录模型"""
    __tablename__ = "inspection_records"
    
    inspector_certificate_number = Column(String(50), ForeignKey("personnel.certificate_number"), nullable=False, comment='查班人员证件号')
    start_time = Column(DateTime(timezone=True), nullable=False, comment='查班开始时间')
    end_time = Column(DateTime(timezone=True), nullable=False, comment='查班结束时间')
    inspection_type = Column(SQLEnum(InspectionType), nullable=False, comment='查班类型')
    duty_record_id = Column(Integer, ForeignKey("duty_records.id"), nullable=False, index=True, comment='执勤记录ID')
    evaluation_level = Column(SQLEnum(EvaluationLevel), default=EvaluationLevel.GOOD, comment='评价等级')
    violation_type_code = Column(String(50), comment='违禁类型代码')
    
    # 索引
    __table_args__ = (
        Index('idx_inspector_time', 'inspector_certificate_number', 'start_time'),
    )
    
    # 关系定义
    inspector = relationship("Personnel", back_populates="inspection_records", foreign_keys=[inspector_certificate_number])
    duty_record = relationship("DutyRecord", back_populates="inspection_records")
    
    def get_inspection_type_text(self):
        """获取查班类型文本"""
        return self.inspection_type.value
    
    def get_evaluation_level_text(self):
        """获取评价等级文本"""
        return self.evaluation_level.value
  
