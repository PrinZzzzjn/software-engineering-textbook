from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.core.base_crud import BaseCRUD
from app.core.logger import log
from app.api.v1.module_duty.workstation.model import Workstation
from app.api.v1.module_duty.workstation.schema import WorkstationCreate, WorkstationUpdate


class WorkstationCRUD(BaseCRUD[Workstation, WorkstationCreate, WorkstationUpdate]):
    """工位数据访问层"""
    
    def __init__(self):
        super().__init__(Workstation)
    
    def get_by_workstation_id(self, db: Session, workstation_id: int) -> Optional[Workstation]:
        """根据工位id获取工位信息"""
        return db.query(Workstation).filter(Workstation.workstation_id == workstation_id).first()
    
    def get_paginated_list(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 10,
        workstation_name: Optional[str] = None,
        dept_code: Optional[int] = None,
        category_code: Optional[int] = None,
        sort_by: str = "create_time",
        order: str = "desc"
    ) -> Dict[str, Any]:
        """分页查询工位列表，支持条件筛选和排序"""
        # 构建查询
        query = db.query(Workstation)
        
        # 添加筛选条件
        if workstation_name:
            query = query.filter(Workstation.workstation_name.contains(workstation_name))
        if dept_code:
            query = query.filter(Workstation.dept_code == dept_code)
        if category_code:
            query = query.filter(Workstation.category_code == category_code)
        
        # 添加排序
        order_column = getattr(Workstation, sort_by, Workstation.create_time)
        if order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        skip = (page - 1) * page_size
        items = query.offset(skip).limit(page_size).all()
        
        # 计算总页数
        pages = (total + page_size - 1) // page_size
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages
        }
    
    def delete_by_workstation_id(self, db: Session, workstation_id: int) -> Optional[Workstation]:
        """通过工位id删除工位"""
        try:
            obj = self.get_by_workstation_id(db, workstation_id)
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except Exception as e:
            db.rollback()
            log.error(f"Failed to delete Workstation with workstation_id {workstation_id}: {str(e)}")
            raise
    
    def exists_by_workstation_id(self, db: Session, workstation_id: int, exclude_id: Optional[int] = None) -> bool:
        """检查工位id是否已存在"""
        query = db.query(Workstation).filter(Workstation.workstation_id == workstation_id)
        if exclude_id is not None:
            query = query.filter(Workstation.id != exclude_id)
        return query.first() is not None


# 创建CRUD实例
workstation_crud = WorkstationCRUD()