from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.api.v1.module_duty.dept.model import Department
from app.api.v1.module_duty.dept.schema import DepartmentCreate, DepartmentUpdate, DepartmentTree
from app.api.v1.module_duty.dept.param import DepartmentQueryParams
from app.api.v1.module_duty.dept.crud import dept_crud
from app.core.exceptions import NotFoundException, BadRequestException, DuplicateResourceException

class DepartmentService:
    """部门管理服务类"""
    
    def __init__(self):
        """初始化部门服务"""
        self.crud = dept_crud
    
    def get_department_by_code(self, db: Session, *, dept_code: int) -> Department:
        """根据部门编码获取部门"""
        dept = self.crud.get_by_code(db, dept_code=dept_code)
        if not dept:
            raise NotFoundException(detail="部门不存在")
        return dept
    
    def create_department(self, db: Session, *, dept_in: DepartmentCreate) -> Department:
        """创建新部门"""
        # 检查部门名称是否已存在
        if self.crud.exists_by_name(db, full_name=dept_in.full_name):
            raise DuplicateResourceException(detail="部门名称已存在")
        
        # 检查部门编码是否已存在
        existing_dept = self.crud.get_by_code(db, dept_code=dept_in.dept_code)
        if existing_dept:
            raise DuplicateResourceException(detail="部门编码已存在")
        
        # 检查父部门是否存在
        if dept_in.parent_dept_code is not None:
            parent_dept = self.crud.get_by_code(db, dept_code=dept_in.parent_dept_code)
            if not parent_dept:
                raise BadRequestException(detail="父部门不存在")
        
        # 创建部门
        dept_data = dept_in.model_dump()
        
        return self.crud.create(db, obj_in=dept_data)
    
    def update_department(self, db: Session, *, dept_code: int, dept_in: DepartmentUpdate) -> Department:
        """更新部门信息"""
        # 获取部门
        dept = self.get_department_by_code(db, dept_code=dept_code)
        
        # 检查更新的部门名称是否与其他部门重复
        if dept_in.full_name and dept_in.full_name != dept.full_name:
            if self.crud.exists_by_name(db, full_name=dept_in.full_name, exclude_code=dept_code):
                raise DuplicateResourceException(detail="部门名称已存在")
        
        # 检查是否将部门设置为自身的子部门
        if dept_in.parent_dept_code == dept_code:
            raise BadRequestException(detail="不能将部门设置为自身的子部门")
        
        # 检查父部门是否存在
        if dept_in.parent_dept_code is not None:
            parent_dept = self.crud.get_by_code(db, dept_code=dept_in.parent_dept_code)
            if not parent_dept:
                raise BadRequestException(detail="父部门不存在")
        
        # 更新部门信息
        update_data = dept_in.model_dump(exclude_unset=True)
        return self.crud.update(db, db_obj=dept, obj_in=update_data)
    
    def delete_department(self, db: Session, *, dept_code: int) -> None:
        """删除部门"""
        # 获取部门
        dept = self.get_department_by_code(db, dept_code=dept_code)
        
        # 检查部门是否有子部门
        if self.crud.has_children(db, dept_code=dept_code):
            raise BadRequestException(detail="部门下有子部门，不能删除")
        
        # 检查部门下是否有人员
        if self.has_personnel(db, dept_code=dept_code):
            raise BadRequestException(detail="部门下有人员，不能删除")
        
        # 删除部门
        self.crud.delete_by_code(db, dept_code=dept_code)
    
    def get_department_list(self, db: Session, *, params: DepartmentQueryParams) -> Dict[str, Any]:
        """获取部门列表"""
        return self.crud.get_paginated(db, params=params)
    
    def has_personnel(self, db: Session, *, dept_code: int) -> bool:
        """检查部门下是否有人员"""
        dept = self.get_department_by_code(db, dept_code=dept_code)
        return len(dept.personnel) > 0
    
    def build_department_tree(self, departments: List[Department], parent_code: Optional[int] = None) -> List[Dict[str, Any]]:
        """构建部门树形结构"""
        tree = []
        for dept in departments:
            if dept.parent_dept_code == parent_code:
                node = {
                    "dept_code": dept.dept_code,
                    "full_name": dept.full_name,
                    "parent_dept_code": dept.parent_dept_code,
                    "children": self.build_department_tree(departments, dept.dept_code)
                }
                tree.append(node)
        return tree
    
    def get_department_tree(self, db: Session, *, root_dept_code: Optional[int] = None) -> List[DepartmentTree]:
        """获取部门树形结构"""
        if root_dept_code is not None:
            # 检查根部门是否存在
            root_dept = self.get_department_by_code(db, dept_code=root_dept_code)
            # 获取该部门及其所有子部门
            all_departments = self.crud.get_all(db)
            # 过滤出相关的部门
            relevant_departments = []
            
            def collect_departments(code: int):
                dept = next((d for d in all_departments if d.dept_code == code), None)
                if dept:
                    relevant_departments.append(dept)
                    # 递归收集子部门
                    children = [d for d in all_departments if d.parent_dept_code == code]
                    for child in children:
                        collect_departments(child.dept_code)
            
            collect_departments(root_dept_code)
            tree_data = self.build_department_tree(relevant_departments, root_dept_code)
        else:
            # 获取所有部门
            all_departments = self.crud.get_all(db)
            tree_data = self.build_department_tree(all_departments)
        
        # 转换为响应模型
        return [DepartmentTree(**node) for node in tree_data]
    
    def get_department_detail(self, db: Session, *, dept_code: int) -> Dict[str, Any]:
        """获取部门详情，包含父部门名称和子部门数量"""
        dept = self.get_department_by_code(db, dept_code=dept_code)
        
        # 获取父部门名称
        parent_dept_name = None
        if dept.parent_dept_code:
            parent_dept = self.crud.get_by_code(db, dept_code=dept.parent_dept_code)
            parent_dept_name = parent_dept.full_name if parent_dept else None
        
        # 获取子部门数量
        children = self.crud.get_children(db, parent_dept_code=dept_code)
        child_count = len(children)
        
        return {
            "dept_code": dept.dept_code,
            "full_name": dept.full_name,
            "address": dept.address,
            "longitude": dept.longitude,
            "latitude": dept.latitude,
            "parent_dept_code": dept.parent_dept_code,
            "parent_dept_name": parent_dept_name,
            "child_count": child_count,
            "create_time": dept.create_time,
            "update_time": dept.update_time
        }

# 创建部门服务实例
dept_service = DepartmentService()