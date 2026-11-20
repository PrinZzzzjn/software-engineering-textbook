from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.logger import logger as log
from app.api.v1.module_duty.dept.model import Department
from app.api.v1.module_duty.dept.schema import DepartmentCreate, DepartmentUpdate
from app.api.v1.module_duty.dept.param import DepartmentQueryParams
from app.core.base_crud import BaseCRUD

class DepartmentCRUD(BaseCRUD[Department, DepartmentCreate, DepartmentUpdate]):
    """部门CRUD操作类"""
    
    def __init__(self):
        """初始化部门CRUD类"""
        super().__init__(Department)
    
    def get_by_code(self, db: Session, *, dept_code: int) -> Optional[Department]:
        """根据部门编码获取部门"""
        return db.query(Department).filter(Department.dept_code == dept_code).first()
    
    def get_by_name(self, db: Session, *, full_name: str) -> Optional[Department]:
        """根据部门名称获取部门"""
        return db.query(Department).filter(Department.full_name == full_name).first()
    
    def get_children(self, db: Session, *, parent_dept_code: int) -> List[Department]:
        """获取子部门列表"""
        return db.query(Department).filter(Department.parent_dept_code == parent_dept_code).all()
    
    def get_all(self, db: Session) -> List[Department]:
        """获取所有部门"""
        return db.query(Department).all()
    
    def get_root_departments(self, db: Session) -> List[Department]:
        """获取所有根部门（没有父部门的部门）"""
        return db.query(Department).filter(Department.parent_dept_code.is_(None)).all()
    
    def exists_by_name(self, db: Session, *, full_name: str, exclude_code: Optional[int] = None) -> bool:
        """检查部门名称是否已存在"""
        query = db.query(Department).filter(Department.full_name == full_name)
        if exclude_code is not None:
            query = query.filter(Department.dept_code != exclude_code)
        return query.first() is not None
    
    def has_children(self, db: Session, *, dept_code: int) -> bool:
        """检查部门是否有子部门"""
        return db.query(Department).filter(Department.parent_dept_code == dept_code).first() is not None
    
    def get_paginated(self, db: Session, *, params: DepartmentQueryParams) -> Dict[str, Any]:
        """根据查询参数分页获取部门列表"""
        # 构建查询
        query = db.query(Department)
        
        # 应用过滤条件
        if params.full_name:
            query = query.filter(Department.full_name.ilike(f"%{params.full_name}%"))
        
        if params.parent_dept_code is not None:
            query = query.filter(Department.parent_dept_code == params.parent_dept_code)
        
        # 应用搜索关键词
        if params.keyword:
            query = query.filter(
                or_(
                    Department.full_name.ilike(f"%{params.keyword}%"),
                    Department.address.ilike(f"%{params.keyword}%")
                )
            )
        
        # 应用排序
        if params.sort_by and params.sort_order:
            order_column = getattr(Department, params.sort_by, Department.dept_code)
            if params.sort_order.lower() == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        else:
            query = query.order_by(Department.dept_code.asc())
        
        # 使用父类的分页方法
        return super().get_paginated(
            db, 
            page=params.page, 
            page_size=params.page_size, 
            query=query
        )
    
    def get_max_dept_code(self, db: Session) -> Optional[int]:
        """获取最大的部门编码"""
        result = db.query(Department.dept_code).order_by(Department.dept_code.desc()).first()
        return result[0] if result else None
    
    def delete_by_code(self, db: Session, *, dept_code: int) -> Optional[Department]:
        """根据部门编码删除部门"""
        try:
            obj = db.query(Department).filter(Department.dept_code == dept_code).first()
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except Exception as e:
            db.rollback()
            log.error(f"Failed to delete {Department.__name__} with dept_code {dept_code}: {str(e)}")
            raise

# 创建部门CRUD实例
dept_crud = DepartmentCRUD()