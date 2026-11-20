from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.core.logger import logger as log
from app.api.v1.module_duty.safe_record.model import SafeBoxRecord
from app.core.base_crud import BaseCRUD

class SafeBoxRecordCRUD(BaseCRUD[SafeBoxRecord, None, Dict[str, Any]]):
    """保险箱记录CRUD操作类"""
    
    def __init__(self):
        """初始化保险箱记录CRUD类"""
        super().__init__(SafeBoxRecord)
    
    def get_by_id(self, db: Session, *, id: int) -> Optional[SafeBoxRecord]:
        """根据ID获取保险箱记录，加载关联对象"""
        return db.query(SafeBoxRecord).options(
            joinedload(SafeBoxRecord.department),
            joinedload(SafeBoxRecord.applicant),
            joinedload(SafeBoxRecord.authorizer)
        ).filter(SafeBoxRecord.id == id).first()
    
    def get_paginated(self, db: Session, *, params: Any) -> Dict[str, Any]:
        """根据查询参数分页获取保险箱记录列表"""
        # 构建查询
        query = db.query(SafeBoxRecord).options(
            joinedload(SafeBoxRecord.department),
            joinedload(SafeBoxRecord.applicant),
            joinedload(SafeBoxRecord.authorizer)
        )
        
        # 应用过滤条件
        if params.start_time:
            query = query.filter(SafeBoxRecord.application_time >= params.start_time)
        
        if params.end_time:
            query = query.filter(SafeBoxRecord.application_time <= params.end_time)
        
        if params.dept_code is not None:
            query = query.filter(SafeBoxRecord.dept_code == params.dept_code)
        
        if params.device_id:
            query = query.filter(SafeBoxRecord.device_id == params.device_id)
        
        if params.applicant_certificate_number:
            query = query.filter(SafeBoxRecord.applicant_certificate_number == params.applicant_certificate_number)
        
        if params.application_type:
            query = query.filter(SafeBoxRecord.application_type == params.application_type)
        
        if params.authorizer_certificate_number:
            query = query.filter(SafeBoxRecord.authorizer_certificate_number == params.authorizer_certificate_number)
        
        if params.authorization_result:
            query = query.filter(SafeBoxRecord.authorization_result == params.authorization_result)
        
        # 应用搜索关键词
        if params.keyword:
            query = query.filter(
                or_(
                    SafeBoxRecord.device_id.ilike(f"%{params.keyword}%"),
                    SafeBoxRecord.applicant_certificate_number.ilike(f"%{params.keyword}%"),
                    SafeBoxRecord.authorizer_certificate_number.ilike(f"%{params.keyword}%")
                )
            )
        
        # 应用排序
        if params.sort_by and params.sort_order:
            order_column = getattr(SafeBoxRecord, params.sort_by, SafeBoxRecord.application_time)
            if params.sort_order.lower() == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        else:
            query = query.order_by(SafeBoxRecord.application_time.desc())
        
        # 使用父类的分页方法
        return super().get_paginated(
            db, 
            page=params.page, 
            page_size=params.page_size, 
            query=query
        )

# 创建保险箱记录CRUD实例
safe_box_record_crud = SafeBoxRecordCRUD()