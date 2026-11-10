from pydantic import Field
from typing import Optional
from datetime import datetime
from app.core.base_params import SearchParams
from app.api.v1.module_duty.inspection_record.model import InspectionType, EvaluationLevel

class InspectionRecordQueryParams(SearchParams):
    """查班记录查询参数"""
    start_date: Optional[datetime] = Field(default=None, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")
    inspector_certificate_number: Optional[str] = Field(default=None, description="查班人员证件号")
    duty_record_id: Optional[int] = Field(default=None, description="执勤记录ID")
    inspection_type: Optional[InspectionType] = Field(default=None, description="查班类型")
    evaluation_level: Optional[EvaluationLevel] = Field(default=None, description="评价等级")