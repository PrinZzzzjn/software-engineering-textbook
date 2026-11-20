from pydantic import Field
from typing import Optional
from datetime import datetime
from app.core.base_params import SearchParams

class EquipmentCabinetRecordQueryParams(SearchParams):
    """设备柜记录查询参数"""
    start_time: Optional[datetime] = Field(default=None, description="申请开始时间")
    end_time: Optional[datetime] = Field(default=None, description="申请结束时间")
    dept_code: Optional[str] = Field(default=None, description="部门编码")
    device_id: Optional[str] = Field(default=None, description="设备ID")
    applicant_certificate_number: Optional[str] = Field(default=None, description="申请人证书编号")
    open_type: Optional[str] = Field(default=None, description="开柜类型")
    open_result: Optional[str] = Field(default=None, description="开柜结果")