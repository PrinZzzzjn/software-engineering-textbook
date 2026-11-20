from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import enum
from app.api.v1.module_duty.equipment_cabinet_record.model import EquipmentCabinetRecord, OpenReasonType, CabinetOpenType, CabinetOpenResult
from app.api.v1.module_duty.equipment_cabinet_record.schema import (
    EquipmentCabinetRecordCreate, EquipmentCabinetRecordUpdate, EnumItem
)
from app.api.v1.module_duty.equipment_cabinet_record.param import EquipmentCabinetRecordQueryParams
from app.api.v1.module_duty.equipment_cabinet_record.crud import equipment_cabinet_record_crud
from app.api.v1.module_duty.dept.model import Department
from app.api.v1.module_duty.personnel.model import Personnel
from app.core.exceptions import NotFoundException, BadRequestException

class EquipmentCabinetRecordService:
    """设备柜记录管理服务类"""
    
    def __init__(self):
        """初始化设备柜记录服务"""
        self.crud = equipment_cabinet_record_crud
    
    def get_equipment_cabinet_record_by_id(self, db: Session, *, id: int) -> EquipmentCabinetRecord:
        """根据ID获取设备柜记录"""
        record = self.crud.get_by_id(db, id=id)
        if not record:
            raise NotFoundException(detail="记录不存在")
        return record
    
    def create_equipment_cabinet_record(self, db: Session, *, record_in: EquipmentCabinetRecordCreate) -> EquipmentCabinetRecord:
        """创建新的设备柜记录"""
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
        
        # 验证并转换开启原因类型
        if record_in.open_reason_type not in [item.value for item in OpenReasonType]:
            raise BadRequestException(detail="开启原因类型无效")
        open_reason_enum = next(item for item in OpenReasonType if item.value == record_in.open_reason_type)
        
        # 验证并转换开柜类型
        if record_in.open_type not in [item.value for item in CabinetOpenType]:
            raise BadRequestException(detail="开柜类型无效")
        open_type_enum = next(item for item in CabinetOpenType if item.value == record_in.open_type)
        
        # 验证并转换开柜结果
        if record_in.open_result not in [item.value for item in CabinetOpenResult]:
            raise BadRequestException(detail="开柜结果无效")
        open_result_enum = next(item for item in CabinetOpenResult if item.value == record_in.open_result)
        
        # 创建记录并设置枚举值
        record_data = record_in.model_dump()
        record_data['open_reason_type'] = open_reason_enum
        record_data['open_type'] = open_type_enum
        record_data['open_result'] = open_result_enum
        
        # 确保关闭时间字段正确处理
        # 如果传入了关闭时间，则保留；否则默认为None
        if 'cabinet_close_time' not in record_data or record_data['cabinet_close_time'] is None:
            # 可以根据业务逻辑决定是否需要设置默认值或进行其他处理
            pass
        
        return self.crud.create(db, obj_in=record_data)
    
    def update_equipment_cabinet_record(self, db: Session, *, id: int, record_in: EquipmentCabinetRecordUpdate) -> EquipmentCabinetRecord:
        """更新设备柜记录"""
        # 获取记录
        record = self.get_equipment_cabinet_record_by_id(db, id=id)
        
        # 检查记录是否已关闭
        if record.cabinet_close_time:
            raise BadRequestException(detail="记录已关闭")
        
        # 准备更新数据
        record_data = record_in.model_dump(exclude_unset=True)
        
        # 处理枚举字段转换
        if 'open_reason_type' in record_data:
            if record_data['open_reason_type'] not in [item.value for item in OpenReasonType]:
                raise BadRequestException(detail="开启原因类型无效")
            record_data['open_reason_type'] = next(item for item in OpenReasonType if item.value == record_data['open_reason_type'])
        
        if 'open_type' in record_data:
            if record_data['open_type'] not in [item.value for item in CabinetOpenType]:
                raise BadRequestException(detail="开柜类型无效")
            record_data['open_type'] = next(item for item in CabinetOpenType if item.value == record_data['open_type'])
        
        if 'open_result' in record_data:
            if record_data['open_result'] not in [item.value for item in CabinetOpenResult]:
                raise BadRequestException(detail="开柜结果无效")
            record_data['open_result'] = next(item for item in CabinetOpenResult if item.value == record_data['open_result'])
        return self.crud.update(db, db_obj=record, obj_in=record_data)
    
    def delete_equipment_cabinet_record(self, db: Session, *, id: int) -> None:
        """删除设备柜记录"""
        # 获取记录
        record = self.get_equipment_cabinet_record_by_id(db, id=id)
        
        # 删除记录
        self.crud.delete(db, id=id)
    
    def get_equipment_cabinet_record_list(self, db: Session, *, params: EquipmentCabinetRecordQueryParams) -> Dict[str, Any]:
        """获取设备柜记录列表"""
        from app.core.logger import logger
        try:
            # 执行分页查询
            result = self.crud.get_paginated(db, params=params)
            return result
        except Exception as e:
            logger.error(f"获取设备柜记录列表时发生错误: {str(e)}")
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
    
    def get_equipment_cabinet_record_detail(self, db: Session, *, id: int) -> Dict[str, Any]:
        """获取设备柜记录详情"""
        try:
            record = self.get_equipment_cabinet_record_by_id(db, id=id)
            
            # 安全获取关联对象属性
            dept_name = ""
            if hasattr(record, 'department') and record.department and hasattr(record.department, 'full_name'):
                dept_name = record.department.full_name
            
            applicant_name = ""
            if hasattr(record, 'applicant') and record.applicant and hasattr(record.applicant, 'full_name'):
                applicant_name = record.applicant.full_name
            
            authorizer_name = ""
            if hasattr(record, 'authorizer') and record.authorizer and hasattr(record.authorizer, 'full_name'):
                authorizer_name = record.authorizer.full_name
            
            # 获取枚举值
            open_reason_type_value = record.open_reason_type.value if hasattr(record.open_reason_type, 'value') else record.open_reason_type
            open_type_value = record.open_type.value if hasattr(record.open_type, 'value') else record.open_type
            open_result_value = record.open_result.value if hasattr(record.open_result, 'value') else record.open_result
            
            return {
                "id": record.id,
                "dept_code": record.dept_code,
                "dept_name": dept_name,
                "device_id": record.device_id,
                "applicant_certificate_number": record.applicant_certificate_number,
                "applicant_name": applicant_name,
                "authorizer_certificate_number": record.authorizer_certificate_number,
                "authorizer_name": authorizer_name,
                "application_time": record.application_time,
                "open_reason_type": open_reason_type_value,
                "open_type": open_type_value,
                "open_result": open_result_value,
                "cabinet_open_time": record.cabinet_open_time,
                "cabinet_close_time": record.cabinet_close_time,
                "device_quantity_change": record.device_quantity_change,
                "create_time": record.create_time,
                "update_time": record.update_time
            }
        except AttributeError as e:
            from app.core.logger import logger
            logger.error(f"获取设备柜记录详情时发生属性错误: {str(e)}")
            raise BadRequestException(detail=f"获取记录详情时发生错误: {str(e)}")
    
    def get_open_reason_types(self) -> List[EnumItem]:
        """获取开启原因类型列表"""
        return [
            EnumItem(code=item.value, name=self._get_enum_name(OpenReasonType, item))
            for item in OpenReasonType
        ]
    
    def get_open_types(self) -> List[EnumItem]:
        """获取开柜类型列表"""
        return [
            EnumItem(code=item.value, name=self._get_enum_name(CabinetOpenType, item))
            for item in CabinetOpenType
        ]
    
    def get_open_results(self) -> List[EnumItem]:
        """获取开柜结果列表"""
        return [
            EnumItem(code=item.value, name=self._get_enum_name(CabinetOpenResult, item))
            for item in CabinetOpenResult
        ]
    
    def _get_enum_name(self, enum_class, enum_value) -> str:
        """获取枚举类型的中文名称"""
        # 定义枚举值到中文名称的映射
        open_reason_type_map = {
            "01": "类型01",
            "02": "类型02",
            "03": "类型03"
        }
        
        cabinet_open_type_map = {
            "01": "值班室开启",
            "02": "钥匙开启",
            "03": "终端控制开启"
        }
        
        cabinet_open_result_map = {
            "01": "正常",
            "02": "拒绝",
            "03": "钥匙开柜"
        }
        
        # 获取枚举值的字符串表示
        if isinstance(enum_value, enum_class):
            value_str = enum_value.value
        else:
            value_str = enum_value
        
        # 根据枚举类返回对应的中文名称
        if enum_class == OpenReasonType:
            return open_reason_type_map.get(value_str, "未知")
        elif enum_class == CabinetOpenType:
            return cabinet_open_type_map.get(value_str, "未知")
        elif enum_class == CabinetOpenResult:
            return cabinet_open_result_map.get(value_str, "未知")
        
        return "未知"

# 创建设备柜记录服务实例
equipment_cabinet_record_service = EquipmentCabinetRecordService()