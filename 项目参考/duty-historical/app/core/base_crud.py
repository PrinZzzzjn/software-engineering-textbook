from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from .base_model import BaseModel as BaseDBModel
from .logger import log

# 定义泛型类型变量
ModelType = TypeVar("ModelType", bound=BaseDBModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """基础CRUD操作类"""
    
    def __init__(self, model: Type[ModelType]):
        """初始化CRUD类，传入SQLAlchemy模型"""
        self.model = model
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """根据ID获取单个对象"""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            log.error(f"Failed to get {self.model.__name__} by id {id}: {str(e)}")
            raise
    
    def get_multi(
        self,
        db: Session,
        *, 
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """获取多个对象，带分页"""
        try:
            return db.query(self.model).offset(skip).limit(limit).all()
        except Exception as e:
            log.error(f"Failed to get multiple {self.model.__name__}: {str(e)}")
            raise
    
    def get_multi_by_ids(self, db: Session, *, ids: List[int]) -> List[ModelType]:
        """根据ID列表获取多个对象"""
        try:
            return db.query(self.model).filter(self.model.id.in_(ids)).all()
        except Exception as e:
            log.error(f"Failed to get {self.model.__name__} by ids {ids}: {str(e)}")
            raise
    
    def create(self, db: Session, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """创建新对象"""
        try:
            # 处理字典或Pydantic模型
            if isinstance(obj_in, dict):
                obj_data = obj_in
            else:
                # 将Pydantic模型转换为字典，排除额外字段
                obj_data = obj_in.model_dump()
            
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            log.error(f"Failed to create {self.model.__name__}: {str(e)}")
            raise
    
    def update(
        self,
        db: Session,
        *, 
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """更新现有对象"""
        try:
            # 处理字典或Pydantic模型
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)
            
            # 更新对象属性
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            log.error(f"Failed to update {self.model.__name__} with id {db_obj.id}: {str(e)}")
            raise
    
    def delete(self, db: Session, *, id: int) -> Optional[ModelType]:
        """删除对象"""
        try:
            obj = db.query(self.model).get(id)
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except Exception as e:
            db.rollback()
            log.error(f"Failed to delete {self.model.__name__} with id {id}: {str(e)}")
            raise
    
    def get_paginated(
        self,
        db: Session,
        *, 
        page: int = 1,
        page_size: int = 10,
        query=None,
        order_by=None
    ) -> Dict[str, Any]:
        """分页查询
        
        返回格式：
        {
            "items": [...],  # 当前页的对象列表
            "total": 100,   # 总记录数
            "page": 1,      # 当前页码
            "page_size": 10,# 每页数量
            "pages": 10     # 总页数
        }
        """
        try:
            # 构建查询
            if query is None:
                query = db.query(self.model)
            
            # 应用排序
            if order_by is None:
                query = query.order_by(desc(self.model.id))
            else:
                query = query.order_by(order_by)
            
            # 计算总数
            total = query.count()
            
            # 应用分页
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
        except Exception as e:
            log.error(f"Failed to get paginated {self.model.__name__}: {str(e)}")
            raise
    
    def get_by_field(self, db: Session, *, field: str, value: Any) -> Optional[ModelType]:
        """根据指定字段获取单个对象"""
        try:
            return db.query(self.model).filter(getattr(self.model, field) == value).first()
        except Exception as e:
            log.error(f"Failed to get {self.model.__name__} by {field}={value}: {str(e)}")
            raise
    
    def get_multi_by_field(
        self,
        db: Session,
        *, 
        field: str,
        value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """根据指定字段获取多个对象"""
        try:
            return db.query(self.model).filter(
                getattr(self.model, field) == value
            ).offset(skip).limit(limit).all()
        except Exception as e:
            log.error(f"Failed to get multiple {self.model.__name__} by {field}={value}: {str(e)}")
            raise