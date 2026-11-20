from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.core.base_schema import BaseSchema
from app.api.v1.module_duty.safe_record.model import ApplicationType, AuthorizationType, AuthorizationResult

# 基础响应模型
class SafeBoxRecordBase(BaseSchema):
    """保险箱记录基础信息"""
    dept_code: str = Field(..., description="部门编码")
    device_id: str = Field(..., min_length=1, max_length=100, description="设备ID")
    applicant_certificate_number: str = Field(..., min_length=1, max_length=50, description="申请人证书编号")
    application_time: datetime = Field(..., description="申请时间")
    application_type: str = Field(..., description="申请类型内码")
    authorizer_certificate_number: str = Field(..., min_length=1, max_length=50, description="授权人证书编号")
    authorization_type: str = Field(..., description="授权类型内码")
    authorization_result: str = Field(..., description="授权结果内码")
    open_time: Optional[datetime] = Field(default=None, description="保险箱开启时间")
    close_time: Optional[datetime] = Field(default=None, description="保险箱关闭时间")
    is_test_mode: bool = Field(default=False, description="是否测试模式")

# 创建保险箱记录请求模型
class SafeBoxRecordCreate(BaseSchema):
    """创建保险箱记录请求"""
    dept_code: str = Field(..., description="部门编码")
    device_id: str = Field(..., min_length=1, max_length=100, description="设备ID")
    applicant_certificate_number: str = Field(..., min_length=1, max_length=50, description="申请人证书编号")
    application_time: datetime = Field(..., description="申请时间")
    application_type: str = Field(..., description="申请类型内码")
    authorizer_certificate_number: str = Field(..., min_length=1, max_length=50, description="授权人证书编号")
    authorization_type: str = Field(..., description="授权类型内码")
    authorization_result: str = Field(..., description="授权结果内码")
    open_time: Optional[datetime] = Field(default=None, description="保险箱开启时间")
    close_time: Optional[datetime] = Field(default=None, description="保险箱关闭时间")
    is_test_mode: bool = Field(default=False, description="是否测试模式")

# 更新保险箱记录请求模型
class SafeBoxRecordUpdate(BaseSchema):
    """更新保险箱记录请求"""
    dept_code: str = Field(..., description="部门编码")
    device_id: str = Field(..., min_length=1, max_length=100, description="设备ID")
    applicant_certificate_number: str = Field(..., min_length=1, max_length=50, description="申请人证书编号")
    application_time: datetime = Field(..., description="申请时间")
    application_type: str = Field(..., description="申请类型内码")
    authorizer_certificate_number: str = Field(..., min_length=1, max_length=50, description="授权人证书编号")
    authorization_type: str = Field(..., description="授权类型内码")
    authorization_result: str = Field(..., description="授权结果内码")
    open_time: Optional[datetime] = Field(default=None, description="保险箱开启时间")
    close_time: Optional[datetime] = Field(default=None, description="保险箱关闭时间")
    is_test_mode: bool = Field(default=False, description="是否测试模式")

# 保险箱记录响应模型
class SafeBoxRecordResponse(BaseSchema):
    """保险箱记录响应"""
    id: int = Field(..., description="记录ID")
    dept_code: str = Field(..., description="部门编码")
    device_id: str = Field(..., description="设备ID")
    applicant_certificate_number: str = Field(..., description="申请人证书编号")
    application_time: datetime = Field(..., description="申请时间")
    application_type: str = Field(..., description="申请类型内码")
    authorizer_certificate_number: str = Field(..., description="授权人证书编号")
    authorization_type: str = Field(..., description="授权类型内码")
    authorization_result: str = Field(..., description="授权结果内码")
    open_time: Optional[datetime] = Field(default=None, description="保险箱开启时间")
    close_time: Optional[datetime] = Field(default=None, description="保险箱关闭时间")
    is_test_mode: bool = Field(default=False, description="是否测试模式")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

# 保险箱记录详情响应模型
class SafeBoxRecordDetailResponse(BaseSchema):
    """保险箱记录详情响应"""
    id: int = Field(..., description="记录ID")
    dept_code: str = Field(..., description="部门编码")
    dept_name: str = Field(..., description="部门名称")
    device_id: str = Field(..., description="设备ID")
    applicant_certificate_number: str = Field(..., description="申请人证书编号")
    applicant_name: str = Field(..., description="申请人姓名")
    applicant_position: Optional[str] = Field(default=None, description="申请人职位")
    application_time: datetime = Field(..., description="申请时间")
    application_type: str = Field(..., description="申请类型内码")
    application_type_name: str = Field(..., description="申请类型名称")
    authorizer_certificate_number: str = Field(..., description="授权人证书编号")
    authorizer_name: str = Field(..., description="授权人姓名")
    authorizer_position: Optional[str] = Field(default=None, description="授权人职位")
    authorization_type: str = Field(..., description="授权类型内码")
    authorization_type_name: str = Field(..., description="授权类型名称")
    authorization_result: str = Field(..., description="授权结果内码")
    authorization_result_name: str = Field(..., description="授权结果名称")
    open_time: Optional[datetime] = Field(default=None, description="保险箱开启时间")
    close_time: Optional[datetime] = Field(default=None, description="保险箱关闭时间")
    duration: Optional[str] = Field(default=None, description="持续时间")
    is_test_mode: bool = Field(default=False, description="是否测试模式")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

# 保险箱记录列表项响应模型
class SafeBoxRecordListItem(BaseSchema):
    """保险箱记录列表项"""
    id: int = Field(..., description="记录ID")
    dept_code: str = Field(..., description="部门编码")
    dept_name: str = Field(..., description="部门名称")
    device_id: str = Field(..., description="设备ID")
    applicant_certificate_number: str = Field(..., description="申请人证书编号")
    applicant_name: str = Field(..., description="申请人姓名")
    application_time: datetime = Field(..., description="申请时间")
    application_type: str = Field(..., description="申请类型内码")
    application_type_name: str = Field(..., description="申请类型名称")
    authorizer_certificate_number: str = Field(..., description="授权人证书编号")
    authorizer_name: str = Field(..., description="授权人姓名")
    authorization_type: str = Field(..., description="授权类型内码")
    authorization_type_name: str = Field(..., description="授权类型名称")
    authorization_result: str = Field(..., description="授权结果内码")
    authorization_result_name: str = Field(..., description="授权结果名称")
    open_time: Optional[datetime] = Field(default=None, description="保险箱开启时间")
    close_time: Optional[datetime] = Field(default=None, description="保险箱关闭时间")
    is_test_mode: bool = Field(default=False, description="是否测试模式")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")



# 枚举类型列表项模型
class EnumItem(BaseSchema):
    """枚举类型列表项"""
    code: str = Field(..., description="编码")
    name: str = Field(..., description="名称")

# 枚举类型列表响应模型
class EnumListResponse(BaseSchema):
    """枚举类型列表响应"""
    items: List[EnumItem] = Field(default_factory=list, description="枚举项列表")
