from pydantic import Field
from typing import Optional
from datetime import datetime
from app.core.base_params import SearchParams

class DutyRecordQueryParams(SearchParams):
    """值班记录查询参数"""
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    personnel_certificate_number: Optional[str] = Field(default=None, description="值班人员证件号")
    workstation_id: Optional[str] = Field(default=None, description="工作地点ID")
    status: Optional[str] = Field(default=None, description="值班状态")
