from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.core.base_schema import BaseSchema

# 部门基础信息模型
class DepartmentBase(BaseSchema):
    """部门基础信息"""
    full_name: str = Field(..., min_length=1, max_length=255, description="部门全称")
    address: Optional[str] = Field(default=None, max_length=500, description="部门地址")
    longitude: Optional[float] = Field(default=None, description="经度")
    latitude: Optional[float] = Field(default=None, description="纬度")
    parent_dept_code: Optional[str] = Field(default=None, description="父部门编码")

# 部门创建请求模型
class DepartmentCreate(DepartmentBase):
    """部门创建请求"""
    dept_code: str = Field(..., description="部门编码")

# 部门更新请求模型
class DepartmentUpdate(BaseSchema):
    """部门更新请求"""
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="部门全称")
    address: Optional[str] = Field(default=None, max_length=500, description="部门地址")
    longitude: Optional[float] = Field(default=None, description="经度")
    latitude: Optional[float] = Field(default=None, description="纬度")
    parent_dept_code: Optional[str] = Field(default=None, description="父部门编码")

# 部门响应模型
class DepartmentResponse(DepartmentBase):
    """部门信息响应"""
    dept_code: str = Field(..., description="部门编码")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

# 部门详情响应模型
class DepartmentDetailResponse(DepartmentResponse):
    """部门详情响应"""
    parent_dept_name: Optional[str] = Field(default=None, description="父部门名称")
    child_count: int = Field(default=0, description="子部门数量")

# 部门列表项模型
class DepartmentListItem(BaseSchema):
    """部门列表项"""
    dept_code: str = Field(..., description="部门编码")
    full_name: str = Field(..., description="部门全称")
    address: Optional[str] = Field(default=None, description="部门地址")
    longitude: Optional[float] = Field(default=None, description="经度")
    latitude: Optional[float] = Field(default=None, description="纬度")
    parent_dept_code: Optional[str] = Field(default=None, description="父部门编码")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

# 部门树形节点模型
class DepartmentTree(BaseSchema):
    """部门树形节点"""
    dept_code: str = Field(..., description="部门编码")
    full_name: str = Field(..., description="部门全称")
    parent_dept_code: Optional[int] = Field(default=None, description="父部门编码")
    children: List['DepartmentTree'] = Field(default_factory=list, description="子部门列表")

# 更新前向引用
DepartmentTree.model_rebuild()