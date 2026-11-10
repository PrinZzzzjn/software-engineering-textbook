from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from datetime import datetime
from app.core.base_crud import BaseCRUD
from app.api.v1.module_duty.inspection_record.model import InspectionRecord, InspectionType, EvaluationLevel
from app.api.v1.module_duty.inspection_record.schema import InspectionRecordCreate, InspectionRecordUpdate
from app.api.v1.module_duty.personnel.model import Personnel
from app.api.v1.module_duty.duty_record.model import DutyRecord

class InspectionRecordCRUD(BaseCRUD[InspectionRecord, InspectionRecordCreate, InspectionRecordUpdate]):
    """查班记录CRUD操作类"""
    
    def __init__(self, db: Session):
        """初始化CRUD类"""
        super().__init__(InspectionRecord)
        self.db = db
    
    def get_by_id(self, id: int) -> Optional[InspectionRecord]:
        """根据ID获取查班记录"""
        return self.db.query(InspectionRecord).options(
            joinedload(InspectionRecord.inspector),
            joinedload(InspectionRecord.duty_record).joinedload(DutyRecord.personnel),
            joinedload(InspectionRecord.duty_record).joinedload(DutyRecord.workstation)
        ).filter(InspectionRecord.id == id).first()
    
    def get_multi(
        self,
        page: int = 1,
        page_size: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        inspector_certificate_number: Optional[str] = None,
        duty_record_id: Optional[int] = None,
        inspection_type: Optional[InspectionType] = None,
        evaluation_level: Optional[EvaluationLevel] = None,
        sort_by: str = "create_time",
        sort_order: str = "desc",
    ) -> tuple[List[Dict[str, Any]], int]:
        """分页获取查班记录列表"""
        # 构建查询
        query = (
            self.db.query(
                InspectionRecord,
                Personnel.name.label('inspector_name'),
                DutyRecord.id.label('duty_record_id')
            )
            .outerjoin(Personnel, InspectionRecord.inspector_certificate_number == Personnel.certificate_number)
            .outerjoin(DutyRecord, InspectionRecord.duty_record_id == DutyRecord.id)
        )
        
        # 添加筛选条件
        filters = []
        if start_date:
            filters.append(InspectionRecord.start_time >= start_date)
        if end_date:
            filters.append(InspectionRecord.end_time <= end_date)
        if inspector_certificate_number:
            filters.append(InspectionRecord.inspector_certificate_number == inspector_certificate_number)
        if duty_record_id:
            filters.append(InspectionRecord.duty_record_id == duty_record_id)
        if inspection_type:
            filters.append(InspectionRecord.inspection_type == inspection_type)
        if evaluation_level:
            filters.append(InspectionRecord.evaluation_level == evaluation_level)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        
        # 动态排序
        order_column = getattr(InspectionRecord, sort_by, InspectionRecord.create_time)
        if sort_order == "asc":
            records = query.order_by(order_column.asc()).offset(offset).limit(page_size).all()
        else:
            records = query.order_by(order_column.desc()).offset(offset).limit(page_size).all()
        
        # 格式化结果
        items = []
        for inspection_record, inspector_name, duty_record_id in records:
            item = inspection_record.__dict__.copy()
            item.pop('_sa_instance_state', None)
            item['inspector_name'] = inspector_name
            item['inspection_type_text'] = inspection_record.get_inspection_type_text()
            item['evaluation_level_text'] = inspection_record.get_evaluation_level_text()
            items.append(item)
        
        return items, total
    
    def get_by_duty_record_id(self, duty_record_id: int) -> List[InspectionRecord]:
        """根据值班记录ID获取关联的查班记录列表"""
        return self.db.query(InspectionRecord).filter(
            InspectionRecord.duty_record_id == duty_record_id
        ).order_by(InspectionRecord.create_time.desc()).all()
    
    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取查班统计信息"""
        # 基础查询
        query = self.db.query(InspectionRecord)
        
        # 添加时间筛选
        if start_date:
            query = query.filter(InspectionRecord.start_time >= start_date)
        if end_date:
            query = query.filter(InspectionRecord.end_time <= end_date)
        
        # 统计数据
        total_records = query.count()
        
        # 按查班类型统计
        type_stats = self.db.query(
            InspectionRecord.inspection_type,
            func.count(InspectionRecord.id).label('count')
        )
        
        if start_date:
            type_stats = type_stats.filter(InspectionRecord.start_time >= start_date)
        if end_date:
            type_stats = type_stats.filter(InspectionRecord.end_time <= end_date)
        
        type_stats = type_stats.group_by(InspectionRecord.inspection_type).all()
        
        # 按评价等级统计
        level_stats = self.db.query(
            InspectionRecord.evaluation_level,
            func.count(InspectionRecord.id).label('count')
        )
        
        if start_date:
            level_stats = level_stats.filter(InspectionRecord.start_time >= start_date)
        if end_date:
            level_stats = level_stats.filter(InspectionRecord.end_time <= end_date)
        
        level_stats = level_stats.group_by(InspectionRecord.evaluation_level).all()
        
        return {
            "total_records": total_records,
            "type_statistics": [
                {
                    "inspection_type": t.inspection_type.value,
                    "inspection_type_text": InspectionType(t.inspection_type).name,
                    "count": t.count
                }
                for t in type_stats
            ],
            "level_statistics": [
                {
                    "evaluation_level": l.evaluation_level.value,
                    "evaluation_level_text": EvaluationLevel(l.evaluation_level).name,
                    "count": l.count
                }
                for l in level_stats
            ]
        }
    
    def check_duty_record_exists(self, duty_record_id: int) -> bool:
        """检查值班记录是否存在"""
        return self.db.query(DutyRecord).filter(DutyRecord.id == duty_record_id).first() is not None