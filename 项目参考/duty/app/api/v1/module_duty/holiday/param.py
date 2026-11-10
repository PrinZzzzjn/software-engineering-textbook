from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from app.api.v1.module_duty.holiday.models import HolidayType


class HolidayQueryParams(BaseModel):
    """节假日查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    start_date: Optional[date] = Field(default=None, description="开始日期")
    end_date: Optional[date] = Field(default=None, description="结束日期")
    is_holiday: Optional[bool] = Field(default=None, description="是否为节假日")
    holiday_type: Optional[HolidayType] = Field(default=None, description="节假日类型")
