from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, distinct
from datetime import datetime
from app.core.base_crud import BaseCRUD
from app.api.v1.module_duty.duty_record.model import DutyRecord
from app.api.v1.module_duty.duty_record.schema import DutyRecordCreate, DutyRecordUpdate
from app.api.v1.module_duty.personnel.model import Personnel
from app.api.v1.module_duty.workstation.model import Workstation
from app.api.v1.module_duty.dept.model import Department

class DutyRecordCRUD(BaseCRUD[DutyRecord, DutyRecordCreate, DutyRecordUpdate]):
    """值班记录CRUD操作类"""
    
    def __init__(self, db: Session):
        """初始化CRUD类"""
        super().__init__(DutyRecord)
        self.db = db
    
    def get_by_id(self, id: int) -> Optional[DutyRecord]:
        """根据ID获取值班记录"""
        return self.db.query(DutyRecord).options(
            joinedload(DutyRecord.personnel),
            joinedload(DutyRecord.successor),
            joinedload(DutyRecord.workstation)
        ).filter(DutyRecord.id == id).first()
    
    def check_time_conflict(self, personnel_certificate_number: str, start_time: datetime, end_time: datetime, exclude_id: Optional[int] = None) -> bool:
        """检查时间冲突"""
        query = self.db.query(DutyRecord).filter(
            DutyRecord.personnel_certificate_number == personnel_certificate_number,
            DutyRecord.status != 'cancelled',
            or_(
                and_(DutyRecord.start_time <= start_time, DutyRecord.end_time > start_time),
                and_(DutyRecord.start_time < end_time, DutyRecord.end_time >= end_time),
                and_(DutyRecord.start_time >= start_time, DutyRecord.end_time <= end_time),
                and_(DutyRecord.start_time <= start_time, DutyRecord.end_time >= end_time)
            )
        )
        
        if exclude_id:
            query = query.filter(DutyRecord.id != exclude_id)
        
        return query.first() is not None
    
    def get_multi(
        self,
        page: int = 1,
        page_size: int = 10,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        personnel_certificate_number: Optional[str] = None,
        workstation_id: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: str = "id",
        sort_order: str = "desc",
    ) -> tuple[List[Dict[str, Any]], int]:
        """分页获取值班记录列表"""
        # 构建查询
        query = (
            self.db.query(
                DutyRecord,
                Personnel.name.label('personnel_name'),
                Workstation.workstation_name.label('workstation_name')
            )
            .outerjoin(Personnel, DutyRecord.personnel_certificate_number == Personnel.certificate_number)
            .outerjoin(Workstation, DutyRecord.workstation_id == Workstation.workstation_id)
        )
        
        # 添加筛选条件
        filters = []
        if start_time:
            filters.append(DutyRecord.start_time >= start_time)
        if end_time:
            filters.append(DutyRecord.end_time <= end_time)
        if personnel_certificate_number:
            filters.append(DutyRecord.personnel_certificate_number == personnel_certificate_number)
        if workstation_id:
            filters.append(DutyRecord.workstation_id == workstation_id)
        if status:
            filters.append(DutyRecord.status == status)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        
        # 动态排序
        order_column = getattr(DutyRecord, sort_by, DutyRecord.start_time)
        if sort_order == "asc":
            records = query.order_by(order_column.asc()).offset(offset).limit(page_size).all()
        else:
            records = query.order_by(order_column.desc()).offset(offset).limit(page_size).all()
        
        # 格式化结果
        items = []
        for duty_record, personnel_name, workstation_name in records:
            item = duty_record.__dict__.copy()
            item.pop('_sa_instance_state', None)
            item['personnel_name'] = personnel_name
            item['workstation_name'] = workstation_name
            items.append(item)
        
        return items, total
    
    def get_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取值班统计信息"""
        # 基础查询
        query = self.db.query(DutyRecord)
        
        # 添加时间筛选
        if start_time:
            query = query.filter(DutyRecord.start_time >= start_time)
        if end_time:
            query = query.filter(DutyRecord.end_time <= end_time)
        
        # 统计数据
        total_records = query.count()
        
        # 按人员统计值班次数
        personnel_stats = self.db.query(
            DutyRecord.personnel_certificate_number,
            Personnel.name,
            func.count(DutyRecord.id).label('duty_count')
        ).outerjoin(
            Personnel, DutyRecord.personnel_certificate_number == Personnel.certificate_number
        )
        
        if start_time:
            personnel_stats = personnel_stats.filter(DutyRecord.start_time >= start_time)
        if end_time:
            personnel_stats = personnel_stats.filter(DutyRecord.end_time <= end_time)
        
        personnel_stats = personnel_stats.group_by(
            DutyRecord.personnel_certificate_number,
            Personnel.name
        ).order_by(func.count(DutyRecord.id).desc()).all()
        
        # 按状态统计
        status_stats = self.db.query(
            DutyRecord.status,
            func.count(DutyRecord.id).label('count')
        )
        
        if start_time:
            status_stats = status_stats.filter(DutyRecord.start_time >= start_time)
        if end_time:
            status_stats = status_stats.filter(DutyRecord.end_time <= end_time)
        
        status_stats = status_stats.group_by(DutyRecord.status).all()
        
        return {
            "total_records": total_records,
            "personnel_statistics": [
                {
                    "personnel_certificate_number": p.personnel_certificate_number,
                    "personnel_name": p.name,
                    "duty_count": p.duty_count
                }
                for p in personnel_stats
            ],
            "status_statistics": [
                {
                    "status": s.status,
                    "count": s.count
                }
                for s in status_stats
            ]
        }
