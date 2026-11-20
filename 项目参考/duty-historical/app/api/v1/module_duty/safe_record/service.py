from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import enum
from app.api.v1.module_duty.safe_record.model import SafeBoxRecord, ApplicationType, AuthorizationType, AuthorizationResult
from app.api.v1.module_duty.safe_record.schema import (
    SafeBoxRecordCreate, SafeBoxRecordUpdate, EnumItem
)
from app.api.v1.module_duty.safe_record.param import SafeBoxRecordQueryParams
from app.api.v1.module_duty.safe_record.crud import safe_box_record_crud
from app.api.v1.module_duty.dept.model import Department
from app.api.v1.module_duty.personnel.model import Personnel
from app.core.exceptions import NotFoundException, BadRequestException

class SafeBoxRecordService:
    """保险箱记录管理服务类"""
    
    def __init__(self):
        """初始化保险箱记录服务"""
        self.crud = safe_box_record_crud
    
    def get_safe_box_record_by_id(self, db: Session, *, id: int) -> SafeBoxRecord:
        """根据ID获取保险箱记录"""
        record = self.crud.get_by_id(db, id=id)
        if not record:
            raise NotFoundException(detail="记录不存在")
        return record
    
    def create_safe_box_record(self, db: Session, *, record_in: SafeBoxRecordCreate) -> SafeBoxRecord:
        """创建新的保险箱记录"""
        # 验证部门是否存在
        dept = db.query(Department).filter(Department.dept_code == record_in.dept_code).first()
        if not dept:
            raise BadRequestException(detail="部门不存在")
        
        # 验证申请人是否存在
        applicant = db.query(Personnel).filter(Personnel.certificate_number == record_in.applicant_certificate_number).first()
        if not applicant:
            raise BadRequestException(detail="申请人不存在")
        
        # 验证授权人是否存在
        authorizer = db.query(Personnel).filter(Personnel.certificate_number == record_in.authorizer_certificate_number).first()
        if not authorizer:
            raise BadRequestException(detail="授权人不存在")
        
        # 验证申请类型
        try:
            ApplicationType(record_in.application_type)
        except ValueError:
            raise BadRequestException(detail="申请类型无效")
        
        # 验证授权类型
        try:
            AuthorizationType(record_in.authorization_type)
        except ValueError:
            raise BadRequestException(detail="授权类型无效")
        
        # 验证授权结果
        try:
            AuthorizationResult(record_in.authorization_result)
        except ValueError:
            raise BadRequestException(detail="授权结果无效")
        
        # 创建记录
        record_data = record_in.model_dump()
        return self.crud.create(db, obj_in=record_data)
    
    def update_safe_box_record(self, db: Session, *, id: int, record_in: SafeBoxRecordUpdate) -> SafeBoxRecord:
        """更新保险箱记录"""
        # 获取记录
        record = self.get_safe_box_record_by_id(db, id=id)
        
        # 验证部门是否存在
        dept = db.query(Department).filter(Department.dept_code == record_in.dept_code).first()
        if not dept:
            raise BadRequestException(detail="部门不存在")
        
        # 验证申请人是否存在
        applicant = db.query(Personnel).filter(Personnel.certificate_number == record_in.applicant_certificate_number).first()
        if not applicant:
            raise BadRequestException(detail="申请人不存在")
        
        # 验证授权人是否存在
        authorizer = db.query(Personnel).filter(Personnel.certificate_number == record_in.authorizer_certificate_number).first()
        if not authorizer:
            raise BadRequestException(detail="授权人不存在")
        
        # 验证申请类型
        try:
            ApplicationType(record_in.application_type)
        except ValueError:
            raise BadRequestException(detail="申请类型无效")
        
        # 验证授权类型
        try:
            AuthorizationType(record_in.authorization_type)
        except ValueError:
            raise BadRequestException(detail="授权类型无效")
        
        # 验证授权结果
        try:
            AuthorizationResult(record_in.authorization_result)
        except ValueError:
            raise BadRequestException(detail="授权结果无效")
        
        # 更新记录
        record_data = record_in.model_dump()
        return self.crud.update(db, db_obj=record, obj_in=record_data)
    
    def delete_safe_box_record(self, db: Session, *, id: int) -> None:
        """删除保险箱记录"""
        # 获取记录
        record = self.get_safe_box_record_by_id(db, id=id)
        
        # 删除记录
        self.crud.delete(db, id=id)
    
    def get_safe_box_record_list(self, db: Session, *, params: SafeBoxRecordQueryParams) -> Dict[str, Any]:
        """获取保险箱记录列表"""
        from app.core.logger import logger
        try:
            # 构建查询条件
            filters = {}
            try:
                if hasattr(params, 'dept_code') and params.dept_code:
                    filters["dept_code"] = params.dept_code
                if hasattr(params, 'device_id') and params.device_id:
                    filters["device_id"] = params.device_id
                if hasattr(params, 'applicant_certificate_number') and params.applicant_certificate_number:
                    filters["applicant_certificate_number"] = params.applicant_certificate_number
                if hasattr(params, 'authorizer_certificate_number') and params.authorizer_certificate_number:
                    filters["authorizer_certificate_number"] = params.authorizer_certificate_number
                if hasattr(params, 'application_type') and params.application_type is not None:
                    filters["application_type"] = params.application_type
                if hasattr(params, 'authorization_type') and params.authorization_type is not None:
                    filters["authorization_type"] = params.authorization_type
                if hasattr(params, 'authorization_result') and params.authorization_result is not None:
                    filters["authorization_result"] = params.authorization_result
                if hasattr(params, 'is_test_mode') and params.is_test_mode is not None:
                    filters["is_test_mode"] = params.is_test_mode
                if hasattr(params, 'start_date') and params.start_date:
                    filters["application_time__gte"] = params.start_date
                if hasattr(params, 'end_date') and params.end_date:
                    filters["application_time__lte"] = params.end_date
            except AttributeError as e:
                logger.error(f"AttributeError when building filters: {str(e)}")
                logger.error(f"Params attributes: {dir(params)}")
                # 使用默认参数继续执行
                pass
            
            # 执行分页查询
            try:
                result = self.crud.get_paginated(
                    db,
                    params=params
                )
                
                # 验证结果结构
                if not isinstance(result, dict) or "items" not in result:
                    logger.error(f"Invalid result structure from get_paginated: {type(result)}")
                    # 返回空结果
                    page = params.page if hasattr(params, 'page') else 1
                    page_size = params.page_size if hasattr(params, 'page_size') else 10
                    return {
                        "items": [],
                        "total": 0,
                        "page": page,
                        "page_size": page_size,
                        "pages": 0
                    }
                
                return result
            except AttributeError as e:
                logger.error(f"AttributeError in get_paginated: {str(e)}")
                # 返回空结果
                page = params.page if hasattr(params, 'page') else 1
                page_size = params.page_size if hasattr(params, 'page_size') else 10
                return {
                    "items": [],
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "pages": 0
                }
        except Exception as e:
            logger.error(f"Unexpected error in get_safe_box_record_list: {str(e)}")
            # 返回空结果，确保API不崩溃
            page = params.page if hasattr(params, 'page') else 1
            page_size = params.page_size if hasattr(params, 'page_size') else 10
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "pages": 0
            }
    
    def get_safe_box_record_detail(self, db: Session, *, id: int) -> Dict[str, Any]:
        """获取保险箱记录详情"""
        try:
            record = self.get_safe_box_record_by_id(db, id=id)
            
            # 计算持续时间
            duration = None
            if record.open_time and record.close_time:
                duration_seconds = (record.close_time - record.open_time).total_seconds()
                hours = int(duration_seconds // 3600)
                minutes = int((duration_seconds % 3600) // 60)
                if hours > 0:
                    duration = f"{hours}小时{minutes}分钟"
                else:
                    duration = f"{minutes}分钟"
            
            # 转换枚举值为名称
            application_type_name = self._get_enum_name(ApplicationType, record.application_type)
            authorization_type_name = self._get_enum_name(AuthorizationType, record.authorization_type)
            authorization_result_name = self._get_enum_name(AuthorizationResult, record.authorization_result)
            
            # 安全获取关联对象属性
            dept_name = ""
            if hasattr(record, 'department') and record.department and hasattr(record.department, 'full_name'):
                dept_name = record.department.full_name
            
            applicant_name = ""
            applicant_position = None
            if hasattr(record, 'applicant') and record.applicant:
                if hasattr(record.applicant, 'full_name'):
                    applicant_name = record.applicant.full_name
                if hasattr(record.applicant, 'position'):
                    applicant_position = record.applicant.position
            
            authorizer_name = ""
            authorizer_position = None
            if hasattr(record, 'authorizer') and record.authorizer:
                if hasattr(record.authorizer, 'full_name'):
                    authorizer_name = record.authorizer.full_name
                if hasattr(record.authorizer, 'position'):
                    authorizer_position = record.authorizer.position
            
            # 获取枚举值
            application_type_value = record.application_type.value if hasattr(record.application_type, 'value') else record.application_type
            authorization_type_value = record.authorization_type.value if hasattr(record.authorization_type, 'value') else record.authorization_type
            authorization_result_value = record.authorization_result.value if hasattr(record.authorization_result, 'value') else record.authorization_result
            
            return {
                "id": record.id,
                "dept_code": record.dept_code,
                "dept_name": dept_name,
                "device_id": record.device_id,
                "applicant_certificate_number": record.applicant_certificate_number,
                "applicant_name": applicant_name,
                "applicant_position": applicant_position,
                "application_time": record.application_time,
                "application_type": application_type_value,
                "application_type_name": application_type_name,
                "authorizer_certificate_number": record.authorizer_certificate_number,
                "authorizer_name": authorizer_name,
                "authorizer_position": authorizer_position,
                "authorization_type": authorization_type_value,
                "authorization_type_name": authorization_type_name,
                "authorization_result": authorization_result_value,
                "authorization_result_name": authorization_result_name,
                "open_time": record.open_time,
                "close_time": record.close_time,
                "duration": duration,
                "is_test_mode": record.is_test_mode,
                "created_at": record.create_time,
                "updated_at": record.update_time
            }
        except AttributeError as e:
            from app.core.logger import logger
            logger.error(f"AttributeError in get_safe_box_record_detail: {str(e)}")
            logger.error(f"Record attributes: {dir(record)}")
            if hasattr(record, 'department'):
                logger.error(f"Department: {record.department}, type: {type(record.department)}")
            if hasattr(record, 'applicant'):
                logger.error(f"Applicant: {record.applicant}, type: {type(record.applicant)}")
            if hasattr(record, 'authorizer'):
                logger.error(f"Authorizer: {record.authorizer}, type: {type(record.authorizer)}")
            raise BadRequestException(detail=f"获取记录详情时发生属性错误: {str(e)}")
    
    def get_application_types(self) -> List[EnumItem]:
        """获取申请类型列表"""
        return [
            EnumItem(code=item.value, name=self._get_enum_name(ApplicationType, item))
            for item in ApplicationType
        ]
    
    def get_authorization_types(self) -> List[EnumItem]:
        """获取授权类型列表"""
        return [
            EnumItem(code=item.value, name=self._get_enum_name(AuthorizationType, item))
            for item in AuthorizationType
        ]
    
    def get_authorization_results(self) -> List[EnumItem]:
        """获取授权结果列表"""
        return [
            EnumItem(code=item.value, name=self._get_enum_name(AuthorizationResult, item))
            for item in AuthorizationResult
        ]
    
    def _get_enum_name(self, enum_class, enum_value) -> str:
        """获取枚举类型的中文名称"""
        # 定义枚举值到中文名称的映射
        application_type_map = {
            "01": "工位申请",
            "02": "值班室供应",
            "03": "联动申请",
            "04": "保险箱控制器",
            "05": "钥匙开启"
        }
        
        authorization_type_map = {
            "01": "值班室授权",
            "02": "联动授权",
            "03": "保险箱控制器",
            "04": "保险箱钥匙",
            "05": "实地供应"
        }
        
        authorization_result_map = {
            "01": "成功",
            "02": "失败",
            "03": "超时",
            "04": "拒绝"
        }
        
        # 获取枚举值的字符串表示
        if isinstance(enum_value, enum_class):
            value_str = enum_value.value
        else:
            value_str = enum_value
        
        # 根据枚举类返回对应的中文名称
        if enum_class == ApplicationType:
            return application_type_map.get(value_str, "未知")
        elif enum_class == AuthorizationType:
            return authorization_type_map.get(value_str, "未知")
        elif enum_class == AuthorizationResult:
            return authorization_result_map.get(value_str, "未知")
        
        return "未知"

# 创建保险箱记录服务实例
safe_box_record_service = SafeBoxRecordService()

