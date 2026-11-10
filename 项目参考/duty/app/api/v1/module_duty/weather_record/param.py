from typing import Optional
from datetime import datetime
from pydantic import Field
from app.core.base_params import BaseParams

class WeatherRecordQueryParams(BaseParams):
    """天气记录查询参数"""
    # 分页参数
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    
    # 时间范围筛选
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    
    # 部门筛选
    dept_code: Optional[str] = Field(default=None, description="部门代码")


class WeatherRecordDeleteByDeptParams(BaseParams):
    """按部门代码删除天气记录参数"""
    # 部门代码，必选参数
    dept_code: str = Field(..., description="部门代码")
    
    # 可选的时间范围筛选
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
