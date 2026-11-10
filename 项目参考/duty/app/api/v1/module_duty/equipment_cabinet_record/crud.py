from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.core.logger import logger as log
from app.api.v1.module_duty.equipment_cabinet_record.model import EquipmentCabinetRecord
from app.core.base_crud import BaseCRUD

class EquipmentCabinetRecordCRUD(BaseCRUD[EquipmentCabinetRecord, None, Dict[str, Any]]):
    """设备柜记录CRUD操作类"""
    
    def __init__(self):
        """初始化设备柜记录CRUD类"""
        super().__init__(EquipmentCabinetRecord)
    
    def get_by_id(self, db: Session, *, id: int) -> Optional[EquipmentCabinetRecord]:
        """根据ID获取设备柜记录，加载关联对象"""
        return db.query(EquipmentCabinetRecord).options(
            joinedload(EquipmentCabinetRecord.department),
            joinedload(EquipmentCabinetRecord.applicant),
            joinedload(EquipmentCabinetRecord.authorizer)
        ).filter(EquipmentCabinetRecord.id == id).first()
    
    def get_paginated(self, db: Session, *, params: Any) -> Dict[str, Any]:
        """根据查询参数分页获取设备柜记录列表"""
        # 构建查询
        query = db.query(EquipmentCabinetRecord).options(
            joinedload(EquipmentCabinetRecord.department),
            joinedload(EquipmentCabinetRecord.applicant),
            joinedload(EquipmentCabinetRecord.authorizer)
        )
        
        # 应用过滤条件
        if params.start_time:
            query = query.filter(EquipmentCabinetRecord.application_time >= params.start_time)
        
        if params.end_time:
            query = query.filter(EquipmentCabinetRecord.application_time <= params.end_time)
        
        if params.dept_code:
            query = query.filter(EquipmentCabinetRecord.dept_code == params.dept_code)
        
        if params.device_id:
            query = query.filter(EquipmentCabinetRecord.device_id == params.device_id)
        
        if params.applicant_certificate_number:
            query = query.filter(EquipmentCabinetRecord.applicant_certificate_number == params.applicant_certificate_number)
        
        if params.open_type:
            query = query.filter(EquipmentCabinetRecord.open_type == params.open_type)
        
        if params.open_result:
            query = query.filter(EquipmentCabinetRecord.open_result == params.open_result)
        
        # 应用搜索关键词
        if params.keyword:
            query = query.filter(
                or_(
                    EquipmentCabinetRecord.device_id.ilike(f"%{params.keyword}%"),
                    EquipmentCabinetRecord.applicant_certificate_number.ilike(f"%{params.keyword}%"),
                    EquipmentCabinetRecord.authorizer_certificate_number.ilike(f"%{params.keyword}%")
                )
            )
        
        # 应用排序
        if params.sort_by and params.sort_order:
            order_column = getattr(EquipmentCabinetRecord, params.sort_by, EquipmentCabinetRecord.application_time)
            if params.sort_order.lower() == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        else:
            query = query.order_by(EquipmentCabinetRecord.application_time.desc())
        
        # 使用父类的分页方法
        return super().get_paginated(
            db, 
            page=params.page, 
            page_size=params.page_size, 
            query=query
        )

# 创建设备柜记录CRUD实例
equipment_cabinet_record_crud = EquipmentCabinetRecordCRUD()