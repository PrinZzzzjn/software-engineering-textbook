from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date, datetime
from app.core.base_schema import BaseSchema


class PersonnelBase(BaseSchema):
    """人员基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    certificate_number: str = Field(..., min_length=1, max_length=50, description="证件号/工号")
    id_card_number: str = Field(..., min_length=18, max_length=18, description="身份证号")
    dept_code: Optional[str] = Field(None, description="部门编码")
    position: Optional[str] = Field(None, max_length=100, description="职务")
    rank: Optional[str] = Field(None, max_length=50, description="职级")
    hire_date: Optional[date] = Field(None, description="入职日期")
    
    @field_validator('id_card_number')
    @classmethod
    def validate_id_card(cls, v):
        """简单验证身份证号格式"""
        if len(v) != 18:
            raise ValueError('身份证号必须为18位')
        # 可以添加更复杂的验证逻辑
        return v


class PersonnelCreate(PersonnelBase):
    """创建人员请求模型"""
    # 创建时所有字段都需要提供
    pass


class PersonnelUpdate(BaseSchema):
    """更新人员请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="姓名")
    dept_code: Optional[str] = Field(None, description="部门编码")
    position: Optional[str] = Field(None, max_length=100, description="职务")
    rank: Optional[str] = Field(None, max_length=50, description="职级")
    
    # 注意：工号和身份证号不应该在更新时修改


class PersonnelInDB(PersonnelBase):
    """数据库中的人员模型"""
    id: int
    create_time: datetime
    update_time: datetime


class PersonnelResponse(PersonnelBase):
    """人员响应模型"""
    id: int
    department_name: Optional[str] = Field(None, description="部门名称")
    create_time: datetime
    update_time: datetime


class PersonnelListResponse(BaseSchema):
    """人员列表响应模型"""
    items: List[PersonnelResponse]
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


class PersonnelImportResult(BaseSchema):
    """人员导入结果响应模型"""
    success_count: int = Field(..., description="成功导入数量")
    failed_count: int = Field(..., description="失败导入数量")
    failed_details: List[dict] = Field(default_factory=list, description="失败详情")


class PersonnelBatchDeleteRequest(BaseSchema):
    """批量删除人员请求模型"""
    certificate_numbers: List[str] = Field(..., description="人员工号列表")
