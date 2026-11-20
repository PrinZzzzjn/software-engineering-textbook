from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# 定义泛型类型变量
DataT = TypeVar("DataT")

# 基础模型配置
class BaseSchema(BaseModel):
    """基础Schema类"""
    model_config = ConfigDict(
        from_attributes=True,  # 支持从ORM模型转换
        populate_by_name=True,  # 支持使用字段别名
        json_encoders={
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }
    )

# 分页响应模型
class PaginatedResponse(BaseModel, Generic[DataT]):
    """分页响应模型"""
    items: List[DataT]
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")

# 基础响应模型
class BaseResponse(BaseModel):
    """基础响应模型"""
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="Success", description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")

# 成功响应模型
class SuccessResponse(BaseResponse):
    """成功响应模型"""
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="Success", description="响应消息")

# 错误响应模型
class ErrorResponse(BaseResponse):
    """错误响应模型"""
    code: int = Field(default=400, description="状态码")
    message: str = Field(default="Error", description="错误消息")
    error: Optional[str] = Field(default=None, description="错误类型")

# ID请求模型
class IDRequest(BaseModel):
    """ID请求模型"""
    id: int = Field(..., description="对象ID")

# ID响应模型
class IDResponse(BaseModel):
    """ID响应模型"""
    id: int = Field(..., description="对象ID")

# 批量ID请求模型
class BatchIDRequest(BaseModel):
    """批量ID请求模型"""
    ids: List[int] = Field(..., description="对象ID列表")

# 批量操作响应模型
class BatchOperationResponse(BaseResponse):
    """批量操作响应模型"""
    success_count: int = Field(..., description="成功操作数量")
    failed_count: int = Field(..., description="失败操作数量")
    failed_ids: Optional[List[int]] = Field(default=None, description="失败的ID列表")

# 通用搜索参数模型
class SearchParams(BaseModel):
    """通用搜索参数模型"""
    keyword: Optional[str] = Field(default=None, description="搜索关键词")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")

# 排序参数
class SortParams(BaseModel):
    """排序参数模型"""
    sort_by: Optional[str] = Field(default="id", description="排序字段")
    sort_order: Optional[str] = Field(default="desc", description="排序方向: asc或desc")