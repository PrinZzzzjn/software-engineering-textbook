from pydantic import Field
from typing import Optional
from app.core.base_params import SearchParams

class DepartmentQueryParams(SearchParams):
    """部门查询参数"""
    full_name: Optional[str] = Field(default=None, description="部门名称搜索")
    parent_dept_code: Optional[int] = Field(default=None, description="父部门编码筛选")
