from typing import Optional
from pydantic import Field
from app.core.base_params import BaseParams


class WorkstationQueryParams(BaseParams):
    """工位查询参数"""
    workstation_name: Optional[str] = Field(None, description="工位名称搜索")
    dept_code: Optional[str] = Field(None, description="单位内码")
    category_code: Optional[str] = Field(None, description="工位类别内码筛选")
    sort_by: str = Field(default="create_time", description="排序字段")
    order: str = Field(default="desc", pattern="^(asc|desc)$", description="排序方式：asc或desc")


class WorkstationListParam(BaseParams):
    """工位列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    workstation_name: Optional[str] = Field(None, description="工位名称，支持模糊搜索")
    dept_code: Optional[str] = Field(None, description="单位内码")
    category_code: Optional[str] = Field(None, description="类别代码")
    sort_by: str = Field("create_time", description="排序字段")
    order: str = Field("desc", pattern="^(asc|desc)$", description="排序方向，asc升序，desc降序")
