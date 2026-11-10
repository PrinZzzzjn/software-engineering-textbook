from typing import Any, Dict, List, Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.core.base_crud import BaseCRUD
from app.core.logger import log
from app.api.v1.module_duty.personnel.model import Personnel
from app.api.v1.module_duty.personnel.schema import PersonnelCreate, PersonnelUpdate
from app.api.v1.module_duty.dept.model import Department


class PersonnelCRUD(BaseCRUD[Personnel, PersonnelCreate, PersonnelUpdate]):
    """人员数据访问层"""
    
    def __init__(self):
        super().__init__(Personnel)
    
    def get_by_certificate_number(self, db: Session, certificate_number: str) -> Optional[Personnel]:
        """根据工号获取人员"""
        return db.query(Personnel).filter(Personnel.certificate_number == certificate_number).first()
    
    def get_by_id_card_number(self, db: Session, id_card_number: str) -> Optional[Personnel]:
        """根据身份证号获取人员"""
        return db.query(Personnel).filter(Personnel.id_card_number == id_card_number).first()
    
    def get_with_dept(self, db: Session, certificate_number: str = None, id: int = None) -> Optional[Personnel]:
        """获取人员信息并关联部门信息，支持通过工号或id查询"""
        query = db.query(Personnel).options(joinedload(Personnel.department))
        if certificate_number:
            return query.filter(Personnel.certificate_number == certificate_number).first()
        elif id:
            return query.filter(Personnel.id == id).first()
        return None
    
    def delete_by_certificate_number(self, db: Session, certificate_number: str) -> Optional[Personnel]:
        """通过工号删除人员"""
        try:
            obj = self.get_by_certificate_number(db, certificate_number)
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except Exception as e:
            db.rollback()
            log.error(f"Failed to delete Personnel with certificate_number {certificate_number}: {str(e)}")
            raise
    
    def get_paginated_list(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 10,
        name: Optional[str] = None,
        dept_code: Optional[int] = None,
        position: Optional[str] = None,
        sort_by: str = "create_time",
        order: str = "desc"
    ) -> Dict[str, Any]:
        """分页查询人员列表，支持条件筛选和排序"""
        # 构建查询
        query = db.query(Personnel).options(joinedload(Personnel.department))
        
        # 添加筛选条件
        if name:
            query = query.filter(Personnel.name.contains(name))
        if dept_code:
            query = query.filter(Personnel.dept_code == dept_code)
        if position:
            query = query.filter(Personnel.position.contains(position))
        
        # 添加排序
        order_column = getattr(Personnel, sort_by, Personnel.create_time)
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
    
    def get_by_dept_id(
        self,
        db: Session,
        dept_code: int,
        page: int = 1,
        page_size: int = 10,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取指定部门下的人员列表"""
        # 构建查询
        query = db.query(Personnel).filter(Personnel.dept_code == dept_code)
        
        # 添加筛选条件
        if name:
            query = query.filter(Personnel.name.contains(name))
        
        # 排序：按创建时间倒序
        query = query.order_by(Personnel.create_time.desc())
        
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
    
    def check_exists_by_dept(self, db: Session, dept_code: int) -> bool:
        """检查指定部门是否有人员"""
        return db.query(Personnel).filter(Personnel.dept_code == dept_code).first() is not None
    
    def get_for_export(
        self,
        db: Session,
        dept_code: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Personnel]:
        """获取导出数据"""
        query = db.query(Personnel).options(joinedload(Personnel.department))
        
        if dept_code:
            query = query.filter(Personnel.dept_code == dept_code)
        if start_date:
            query = query.filter(Personnel.hire_date >= start_date)
        if end_date:
            query = query.filter(Personnel.hire_date <= end_date)
        
        return query.order_by(Personnel.create_time.desc()).all()


# 创建CRUD实例
personnel_crud = PersonnelCRUD()
