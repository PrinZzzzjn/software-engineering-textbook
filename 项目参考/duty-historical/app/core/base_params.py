from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from .base_schema import BaseSchema

class BaseParams(BaseSchema):
    """基础查询参数类"""
    pass

class DateRangeParams(BaseParams):
    """日期范围查询参数"""
    start_date: Optional[date] = Field(default=None, description="开始日期")
    end_date: Optional[date] = Field(default=None, description="结束日期")
    
class DateTimeRangeParams(BaseParams):
    """时间范围查询参数"""
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")

class IDParams(BaseParams):
    """ID查询参数"""
    id: int = Field(..., description="对象ID")

class IDsParams(BaseParams):
    """ID列表查询参数"""
    ids: List[int] = Field(..., description="对象ID列表")

class PageParams(BaseParams):
    """分页查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    
class SortParams(BaseParams):
    """排序查询参数"""
    sort_by: str = Field(default="id", description="排序字段")
    sort_order: str = Field(default="desc", description="排序方向: asc或desc")

class SearchParams(PageParams, SortParams):
    """搜索查询参数"""
    keyword: Optional[str] = Field(default=None, description="搜索关键词")
    
class StatusParams(BaseParams):
    """状态查询参数"""
    status: Optional[Union[int, str, bool]] = Field(default=None, description="状态值")
    
class BatchOperationParams(BaseParams):
    """批量操作参数"""
    ids: List[int] = Field(..., description="要操作的对象ID列表")
    
class FilterParams(BaseParams):
    """通用过滤参数"""
    filters: Optional[Dict[str, Any]] = Field(default=None, description="过滤条件字典")
    
class ExportParams(BaseParams):
    """导出参数"""
    format: str = Field(default="json", description="导出格式: json, csv, excel")
    fields: Optional[List[str]] = Field(default=None, description="要导出的字段列表")