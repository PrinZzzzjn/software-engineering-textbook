from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.core.base_schema import BaseSchema

# 基础响应模型
class EquipmentCabinetRecordBase(BaseSchema):
    """设备柜记录基础信息"""
    dept_code: str = Field(..., description="部门编码")
    device_id: str = Field(..., min_length=1, max_length=100, description="设备ID")
    open_reason_type: str = Field(..., description="开启原因内码")
    applicant_certificate_number: str = Field(..., min_length=1, max_length=50, description="申请人证书编号")
    application_time: datetime = Field(..., description="申请时间")
    authorizer_certificate_number: str = Field(..., min_length=1, max_length=50, description="授权人证书编号")
    open_type: str = Field(..., description="开柜类型内码")
    open_result: str = Field(..., description="开柜结果内码")
    cabinet_open_time: Optional[datetime] = Field(default=None, description="设备柜开启时间")
    device_quantity_change: Optional[str] = Field(default=None, description="设备数量变化")

# 创建设备柜记录请求模型
class EquipmentCabinetRecordCreate(BaseSchema):
    """创建设备柜记录请求"""
    dept_code: str = Field(..., description="部门编码")
    device_id: str = Field(..., min_length=1, max_length=100, description="设备ID")
    open_reason_type: str = Field(..., description="开启原因内码")
    applicant_certificate_number: str = Field(..., min_length=1, max_length=50, description="申请人证书编号")
    application_time: datetime = Field(..., description="申请时间")
    authorizer_certificate_number: str = Field(..., min_length=1, max_length=50, description="授权人证书编号")
    open_type: str = Field(..., description="开柜类型内码")
    open_result: str = Field(..., description="开柜结果内码")
    cabinet_open_time: Optional[datetime] = Field(default=None, description="设备柜开启时间")
    cabinet_close_time: Optional[datetime] = Field(default=None, description="设备柜关闭时间")
    device_quantity_change: Optional[str] = Field(default=None, description="设备数量变化")

# 更新设备柜记录请求模型
class EquipmentCabinetRecordUpdate(BaseSchema):
    """更新设备柜记录请求"""
    cabinet_close_time: Optional[datetime] = Field(default=None, description="设备柜关闭时间")
    device_quantity_change: Optional[str] = Field(default=None, description="设备数量变化")

# 设备柜记录响应模型
class EquipmentCabinetRecordResponse(BaseSchema):
    """设备柜记录响应"""
    id: int = Field(..., description="记录ID")
    dept_code: str = Field(..., description="部门编码")
    device_id: str = Field(..., description="设备ID")
    open_reason_type: str = Field(..., description="开启原因内码")
    applicant_certificate_number: str = Field(..., description="申请人证书编号")
    application_time: datetime = Field(..., description="申请时间")
    authorizer_certificate_number: str = Field(..., description="授权人证书编号")
    open_type: str = Field(..., description="开柜类型内码")
    open_result: str = Field(..., description="开柜结果内码")
    cabinet_open_time: Optional[datetime] = Field(default=None, description="设备柜开启时间")
    cabinet_close_time: Optional[datetime] = Field(default=None, description="设备柜关闭时间")
    device_quantity_change: Optional[str] = Field(default=None, description="设备数量变化")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

# 设备柜记录详情响应模型
class EquipmentCabinetRecordDetailResponse(BaseSchema):
    """设备柜记录详情响应"""
    id: int = Field(..., description="记录ID")
    dept_code: str = Field(..., description="部门编码")
    dept_name: str = Field(..., description="部门名称")
    device_id: str = Field(..., description="设备ID")
    applicant_certificate_number: str = Field(..., description="申请人证书编号")
    applicant_name: str = Field(..., description="申请人姓名")
    authorizer_certificate_number: str = Field(..., description="授权人证书编号")
    authorizer_name: str = Field(..., description="授权人姓名")
    application_time: datetime = Field(..., description="申请时间")
    open_reason_type: str = Field(..., description="开启原因内码")
    open_type: str = Field(..., description="开柜类型内码")
    open_result: str = Field(..., description="开柜结果内码")
    cabinet_open_time: Optional[datetime] = Field(default=None, description="设备柜开启时间")
    cabinet_close_time: Optional[datetime] = Field(default=None, description="设备柜关闭时间")
    device_quantity_change: Optional[str] = Field(default=None, description="设备数量变化")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

# 设备柜记录列表项响应模型
class EquipmentCabinetRecordListItem(BaseSchema):
    """设备柜记录列表项"""
    id: int = Field(..., description="记录ID")
    dept_code: str = Field(..., description="部门编码")
    dept_name: str = Field(..., description="部门名称")
    device_id: str = Field(..., description="设备ID")
    applicant_certificate_number: str = Field(..., description="申请人证书编号")
    applicant_name: str = Field(..., description="申请人姓名")
    authorizer_certificate_number: str = Field(..., description="授权人证书编号")
    authorizer_name: str = Field(..., description="授权人姓名")
    application_time: datetime = Field(..., description="申请时间")
    open_reason_type: str = Field(..., description="开启原因内码")
    open_type: str = Field(..., description="开柜类型内码")
    open_result: str = Field(..., description="开柜结果内码")
    cabinet_open_time: Optional[datetime] = Field(default=None, description="设备柜开启时间")
    cabinet_close_time: Optional[datetime] = Field(default=None, description="设备柜关闭时间")
    device_quantity_change: Optional[str] = Field(default=None, description="设备数量变化")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

# 枚举类型列表项模型
class EnumItem(BaseSchema):
    """枚举类型列表项"""
    code: str = Field(..., description="编码")
    name: str = Field(..., description="名称")

# 枚举类型列表响应模型
class EnumListResponse(BaseSchema):
    """枚举类型列表响应"""
    items: List[EnumItem] = Field(default_factory=list, description="枚举项列表")