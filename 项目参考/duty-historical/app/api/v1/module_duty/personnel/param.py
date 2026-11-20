from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from app.core.base_schema import BaseSchema


class PersonnelQueryParams(BaseSchema):
    """人员查询参数模型"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    name: Optional[str] = Field(default=None, description="人员姓名搜索")
    dept_code: Optional[int] = Field(default=None, description="部门编码筛选")
    position: Optional[str] = Field(default=None, description="职位搜索")
    sort_by: Optional[str] = Field(default="created_at", description="排序字段")
    order: Optional[str] = Field(default="desc", description="排序方式: asc或desc")


class PersonnelExportParams(BaseSchema):
    """人员导出参数模型"""
    dept_code: Optional[int] = Field(default=None, description="部门编码筛选")
    start_date: Optional[date] = Field(default=None, description="入职开始日期")
    end_date: Optional[date] = Field(default=None, description="入职结束日期")


class PersonnelDeptQueryParams(BaseSchema):
    """部门下人员查询参数模型"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    name: Optional[str] = Field(default=None, description="人员姓名搜索")
