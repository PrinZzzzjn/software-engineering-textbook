# 节假日Schema - 避免循环导入
from pydantic import BaseModel, Field
from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class HolidayType(str, Enum):
    """节假日类型枚举"""
    LEGAL_HOLIDAY = "01"
    WEEKEND = "02"
    SPECIAL_HOLIDAY = "03"


class HolidayBase(BaseModel):
    """节假日基础模型"""
    date: date
    is_holiday: bool = True
    holiday_type: Optional[HolidayType] = None
    name: Optional[str] = None
    description: Optional[str] = None


class HolidayCreate(HolidayBase):
    """创建节假日请求模型"""
    pass


class HolidayUpdate(BaseModel):
    """更新节假日请求模型"""
    is_holiday: Optional[bool] = None
    holiday_type: Optional[HolidayType] = None
    name: Optional[str] = None
    description: Optional[str] = None


class Holiday(HolidayBase):
    """节假日响应模型"""
    id: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None


class HolidayListResponse(BaseModel):
    """节假日列表响应模型"""
    total: int
    page: int
    page_size: int
    items: List[Holiday]


class HolidayCheckResponse(BaseModel):
    """节假日检查响应模型"""
    date: str
    is_holiday: bool
    holiday_info: Optional[Dict[str, Any]] = None


class ImportResult(BaseModel):
    """导入结果模型"""
    success_count: int
    failed_count: int
    failed_details: List[Dict[str, Any]]
