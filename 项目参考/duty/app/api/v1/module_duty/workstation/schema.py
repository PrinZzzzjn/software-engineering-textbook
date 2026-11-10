from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.core.base_schema import BaseSchema


class WorkstationBase(BaseSchema):
    """工位基础模型"""
    workstation_id: str = Field(..., description="工位id")
    workstation_name: str = Field(..., description="工位名称", max_length=100)
    dept_code: str = Field(..., description="单位内码")
    category_code: Optional[str] = Field(None, description="工位类别内码")
    longitude: Optional[float] = Field(None, description="经度")
    latitude: Optional[float] = Field(None, description="纬度")
    remark: Optional[str] = Field(None, description="备注", max_length=500)


class WorkstationCreate(WorkstationBase):
    """创建工位请求模型"""
    pass


class WorkstationUpdate(BaseSchema):
    """更新工位请求模型"""
    workstation_name: Optional[str] = Field(None, description="工位名称")
    dept_code: Optional[str] = Field(None, description="单位内码")
    category_code: Optional[str] = Field(None, description="工位类别内码")
    longitude: Optional[float] = Field(None, description="经度")
    latitude: Optional[float] = Field(None, description="纬度")
    remark: Optional[str] = Field(None, description="备注")


class WorkstationResponse(WorkstationBase):
    """工位响应模型"""
    id: int = Field(..., description="主键ID")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class WorkstationBatchDeleteRequest(BaseSchema):
    """批量删除工位请求模型"""
    workstation_ids: List[int] = Field(..., description="工位ID列表")


class WorkstationListResponse(BaseSchema):
    """工位列表响应模型"""
    items: list[WorkstationResponse] = Field(..., description="工位列表数据")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页记录数")
    pages: int = Field(..., description="总页数")
