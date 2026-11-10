from typing import Any, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.api.v1.module_duty.workstation.crud import workstation_crud
from app.api.v1.module_duty.dept.crud import dept_crud as department_crud
from app.api.v1.module_duty.workstation.schema import (
    WorkstationCreate, WorkstationUpdate, WorkstationResponse
)
from app.core.logger import log


class WorkstationService:
    """工位管理业务逻辑层"""
    
    def __init__(self):
        self.crud = workstation_crud
    
    def create_workstation(self, db: Session, obj_in: WorkstationCreate) -> WorkstationResponse:
        """创建工位"""
        try:
            # 检查工位id是否已存在
            if self.crud.exists_by_workstation_id(db, obj_in.workstation_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="工位id已存在"
                )
            
            # 检查部门是否存在
            dept = department_crud.get_by_code(db, dept_code=obj_in.dept_code)
            if dept is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="部门不存在"
                )
            
            # 创建工位
            db_workstation = self.crud.create(db, obj_in=obj_in.model_dump())
            
            # 转换为响应模型
            return self._to_response_model(db_workstation)
            
        except HTTPException:
            raise
        except Exception as e:
            log.error(f"创建工位失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建工位失败，请稍后重试"
            )
    
    def get_workstation(self, db: Session, workstation_id: str) -> WorkstationResponse:
        """获取单个工位信息"""
        workstation = self.crud.get_by_workstation_id(db, workstation_id)
        if not workstation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工位不存在"
            )
        return self._to_response_model(workstation)
    
    def update_workstation(self, db: Session, workstation_id: str, obj_in: WorkstationUpdate) -> WorkstationResponse:
        """更新工位信息"""
        try:
            # 检查工位是否存在
            workstation = self.crud.get_by_workstation_id(db, workstation_id)
            if not workstation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="工位不存在"
                )
            
            # 如果更新部门，检查部门是否存在
            if hasattr(obj_in, 'dept_code') and obj_in.dept_code is not None:
                dept = department_crud.get_by_code(db, dept_code=obj_in.dept_code)
                if not dept:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="部门不存在"
                    )
            
            # 更新工位信息
            db_workstation = self.crud.update(db, db_obj=workstation, obj_in=obj_in.model_dump(exclude_unset=True))
            
            return self._to_response_model(db_workstation)
            
        except HTTPException:
            raise
        except Exception as e:
            log.error(f"更新工位失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新工位失败，请稍后重试"
            )
    
    def delete_workstation(self, db: Session, workstation_id: str) -> Dict[str, str]:
        """删除工位"""
        try:
            # 检查工位是否存在
            workstation = self.crud.get_by_workstation_id(db, workstation_id)
            if not workstation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="工位不存在"
                )
            
            # 检查是否有关联的值班记录（这里需要根据实际的关联关系来判断）
            # 简化实现，假设可以直接删除
            # 实际项目中可能需要检查关联记录
            
            # 删除工位
            self.crud.delete_by_workstation_id(db, workstation_id=workstation_id)
            
            return {"message": "工位删除成功"}
            
        except HTTPException:
            raise
        except Exception as e:
            log.error(f"删除工位失败: {str(e)}")
            # 检查是否因为外键约束导致删除失败
            if "foreign key constraint" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="工位存在关联记录，不能删除"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除工位失败，请稍后重试"
            )
    
    def get_workstation_list(self, db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取工位列表"""
        try:
            result = self.crud.get_paginated_list(
                db,
                page=params.get("page", 1),
                page_size=params.get("page_size", 10),
                workstation_name=params.get("workstation_name"),
                dept_code=params.get("dept_code"),
                category_code=params.get("category_code"),
                sort_by=params.get("sort_by", "create_time"),
                order=params.get("order", "desc")
            )
            
            # 转换为响应模型
            result["items"] = [self._to_response_model(item) for item in result["items"]]
            
            return result
            
        except Exception as e:
            log.error(f"获取工位列表失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取工位列表失败，请稍后重试"
            )
    
    def _to_response_model(self, db_workstation: Any) -> WorkstationResponse:
        """将数据库模型转换为响应模型"""
        return WorkstationResponse(
            id=db_workstation.id,
            workstation_id=db_workstation.workstation_id,
            workstation_name=db_workstation.workstation_name,
            dept_code=db_workstation.dept_code,
            category_code=db_workstation.category_code,
            longitude=db_workstation.longitude,
            latitude=db_workstation.latitude,
            remark=db_workstation.remark,
            create_time=db_workstation.create_time,
            update_time=db_workstation.update_time
        )


# 创建服务实例
workstation_service = WorkstationService()