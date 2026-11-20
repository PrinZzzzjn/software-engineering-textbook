from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.core.base_schema import BaseSchema
from app.api.v1.module_duty.inspection_record.model import InspectionType, EvaluationLevel

# 基础响应模型
class InspectionRecordBase(BaseSchema):
    """查班记录基础模型"""
    inspector_certificate_number: str = Field(..., description="查班人员证件号")
    start_time: datetime = Field(..., description="查班开始时间")
    end_time: datetime = Field(..., description="查班结束时间")
    inspection_type: InspectionType = Field(..., description="查班类型")
    duty_record_id: int = Field(..., description="执勤记录ID")
    evaluation_level: EvaluationLevel = Field(default=EvaluationLevel.GOOD, description="评价等级")
    violation_type_code: Optional[str] = Field(None, description="违禁类型代码")

# 创建请求模型
class InspectionRecordCreate(BaseSchema):
    """创建查班记录请求模型"""
    duty_record_id: int = Field(..., description="执勤记录ID")
    start_time: datetime = Field(..., description="查班开始时间")
    end_time: datetime = Field(..., description="查班结束时间")
    inspection_type: InspectionType = Field(..., description="查班类型")
    evaluation_level: EvaluationLevel = Field(default=EvaluationLevel.GOOD, description="评价等级")
    violation_type_code: Optional[str] = Field(None, description="违禁类型代码")

# 更新请求模型
class InspectionRecordUpdate(BaseSchema):
    """更新查班记录请求模型"""
    start_time: Optional[datetime] = Field(None, description="查班开始时间")
    end_time: Optional[datetime] = Field(None, description="查班结束时间")
    inspection_type: Optional[InspectionType] = Field(None, description="查班类型")
    evaluation_level: Optional[EvaluationLevel] = Field(None, description="评价等级")
    violation_type_code: Optional[str] = Field(None, description="违禁类型代码")

# 响应模型
class InspectionRecordResponse(BaseSchema):
    """查班记录响应模型"""
    id: int = Field(..., description="记录ID")
    duty_record_id: int = Field(..., description="执勤记录ID")
    inspector_certificate_number: str = Field(..., description="查班人员证件号")
    inspector_name: Optional[str] = Field(None, description="查班人员姓名")
    start_time: datetime = Field(..., description="查班开始时间")
    end_time: datetime = Field(..., description="查班结束时间")
    inspection_type: InspectionType = Field(..., description="查班类型")
    evaluation_level: EvaluationLevel = Field(..., description="评价等级")
    violation_type_code: Optional[str] = Field(None, description="违禁类型代码")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True

# 详细响应模型中的值班信息
class DutyInfo(BaseSchema):
    """值班信息模型"""
    start_time: datetime = Field(..., description="值班开始时间")
    end_time: datetime = Field(..., description="值班结束时间")
    workstation_id: Optional[str] = Field(None, description="工作地点ID")
    personnel_certificate_number: str = Field(..., description="值班人员证件号")
    personnel_name: Optional[str] = Field(None, description="值班人员姓名")

# 详细响应模型（包含更多关联信息）
class InspectionRecordDetailResponse(InspectionRecordResponse):
    """查班记录详细响应模型"""
    duty_info: Optional[DutyInfo] = Field(None, description="值班信息")

# 分页响应模型
class InspectionRecordListResponse(BaseSchema):
    """查班记录列表响应模型"""
    items: List[InspectionRecordResponse] = Field(..., description="查班记录列表")
    total: int = Field(..., description="总条数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    pages: Optional[int] = Field(None, description="总页数")