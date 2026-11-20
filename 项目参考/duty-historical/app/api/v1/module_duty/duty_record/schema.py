from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.base_schema import BaseSchema

# 基础响应模型
class DutyRecordBase(BaseSchema):
    """值班记录基础模型"""
    personnel_certificate_number: str = Field(..., description="值班人员证件号")
    successor_certificate_number: Optional[str] = Field(None, description="接班人员证件号")
    workstation_id: Optional[str] = Field(None, description="值班工位id")
    start_time: datetime = Field(..., description="值班开始时间")
    end_time: datetime = Field(..., description="值班结束时间")
    status: str = Field(default="normal", description="值班状态")
    remark: Optional[str] = Field(None, description="备注")

# 创建请求模型
class DutyRecordCreate(DutyRecordBase):
    """创建值班记录请求模型"""
    created_by: Optional[str] = Field(None, description="创建人")

# 更新请求模型
class DutyRecordUpdate(BaseSchema):
    """更新值班记录请求模型"""
    successor_certificate_number: Optional[str] = Field(None, description="接班人员证件号")
    workstation_id: Optional[str] = Field(None, description="值班工位id")
    start_time: Optional[datetime] = Field(None, description="值班开始时间")
    end_time: Optional[datetime] = Field(None, description="值班结束时间")
    status: Optional[str] = Field(None, description="值班状态")
    remark: Optional[str] = Field(None, description="备注")

# 响应模型
class DutyRecordResponse(DutyRecordBase):
    """值班记录响应模型"""
    id: int = Field(..., description="记录ID")
    personnel_name: Optional[str] = Field(None, description="值班人员姓名")
    successor_name: Optional[str] = Field(None, description="接班人员姓名")
    workstation_name: Optional[str] = Field(None, description="工作地点名称")
    created_by: Optional[str] = Field(None, description="创建人")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True

# 详细响应模型（包含更多关联信息）
class DutyRecordDetailResponse(DutyRecordResponse):
    """值班记录详细响应模型"""
    personnel_info: Optional[Dict[str, Any]] = Field(None, description="值班人员信息")
    inspection_records: Optional[list] = Field(None, description="查班记录列表")

# 分页响应模型
class DutyRecordListResponse(BaseSchema):
    """值班记录列表响应模型"""
    items: list[DutyRecordResponse] = Field(..., description="值班记录列表")
    total: int = Field(..., description="总条数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    pages: Optional[int] = Field(None, description="总页数")
