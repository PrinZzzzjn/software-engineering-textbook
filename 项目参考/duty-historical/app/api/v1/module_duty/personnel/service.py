from typing import Any, Dict, List, Optional
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import pandas as pd
from io import BytesIO
from app.api.v1.module_duty.personnel.crud import personnel_crud
from app.api.v1.module_duty.personnel.schema import (
    PersonnelCreate, PersonnelUpdate, PersonnelResponse, PersonnelImportResult
)
from app.api.v1.module_duty.dept.crud import dept_crud as department_crud
from app.core.logger import log


class PersonnelService:
    """人员管理业务逻辑层"""
    
    def __init__(self):
        self.crud = personnel_crud
    
    def create_personnel(self, db: Session, obj_in: PersonnelCreate) -> PersonnelResponse:
        """创建人员"""
        try:
            # 检查工号是否已存在
            existing_by_cert = self.crud.get_by_certificate_number(db, obj_in.certificate_number)
            if existing_by_cert:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="工号已存在"
                )
            
            # 检查身份证号是否已存在
            existing_by_id_card = self.crud.get_by_id_card_number(db, obj_in.id_card_number)
            if existing_by_id_card:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="身份证号已存在"
                )
            
            # 如果指定了部门，检查部门是否存在
            if obj_in.dept_code is not None:
                dept = department_crud.get_by_code(db, dept_code=obj_in.dept_code)
                if not dept:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="部门不存在"
                    )
            
            # 创建人员
            db_personnel = self.crud.create(db, obj_in=obj_in.model_dump())
            
            # 获取完整信息（包含部门名称）- 使用工号查询而不是id
            full_info = self.crud.get_with_dept(db, certificate_number=db_personnel.certificate_number)
            
            # 如果获取不到完整信息，使用创建的人员对象作为后备
            if not full_info:
                full_info = db_personnel
            
            # 转换为响应模型
            return self._to_response_model(full_info)
            
        except HTTPException:
            raise
        except Exception as e:
            log.error(f"创建人员失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建人员失败，请稍后重试"
            )
    
    def get_personnel(self, db: Session, certificate_number: str) -> PersonnelResponse:
        """获取单个人员信息"""
        personnel = self.crud.get_with_dept(db, certificate_number=certificate_number)
        if not personnel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="人员不存在"
            )
        return self._to_response_model(personnel)
    
    def update_personnel(self, db: Session, certificate_number: str, obj_in: PersonnelUpdate) -> PersonnelResponse:
        """更新人员信息"""
        try:
            # 检查人员是否存在
            personnel = self.crud.get_by_certificate_number(db, certificate_number)
            if not personnel:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="人员不存在"
                )
            
            # 如果更新部门，检查部门是否存在
            if obj_in.dept_code is not None:
                dept = department_crud.get_by_code(db, dept_code=obj_in.dept_code)
                if not dept:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="部门不存在"
                    )
            
            # 更新人员信息
            db_personnel = self.crud.update(db, db_obj=personnel, obj_in=obj_in.model_dump(exclude_unset=True))
            
            # 获取完整信息
            full_info = self.crud.get_with_dept(db, certificate_number=certificate_number)
            
            return self._to_response_model(full_info)
            
        except HTTPException:
            raise
        except Exception as e:
            log.error(f"更新人员失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新人员失败，请稍后重试"
            )
    
    def delete_personnel(self, db: Session, certificate_number: str) -> Dict[str, str]:
        """删除人员"""
        try:
            # 检查人员是否存在
            personnel = self.crud.get_by_certificate_number(db, certificate_number)
            if not personnel:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="人员不存在"
                )
            
            # 检查是否有值班记录（这里需要根据实际的关联关系来判断）
            # 简化实现，假设可以直接删除
            # 实际项目中可能需要检查关联记录
            
            # 删除人员
            self.crud.delete_by_certificate_number(db, certificate_number=certificate_number)
            
            return {"message": "人员删除成功"}
            
        except HTTPException:
            raise
        except Exception as e:
            log.error(f"删除人员失败: {str(e)}")
            # 检查是否因为外键约束导致删除失败
            if "foreign key constraint" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="人员存在关联记录，不能删除"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除人员失败，请稍后重试"
            )
    
    def get_personnel_list(self, db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取人员列表"""
        try:
            result = self.crud.get_paginated_list(
                db,
                page=params.get("page", 1),
                page_size=params.get("page_size", 10),
                name=params.get("name"),
                dept_code=params.get("department_id"),
                position=params.get("position"),
                sort_by=params.get("sort_by", "create_time"),
                order=params.get("order", "desc")
            )
            
            # 转换为响应模型
            result["items"] = [self._to_response_model(item) for item in result["items"]]
            
            return result
            
        except Exception as e:
            log.error(f"获取人员列表失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取人员列表失败，请稍后重试"
            )
    
    def get_personnel_by_dept(self, db: Session, dept_code: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取部门下的人员列表"""
        try:
            # 检查部门是否存在
            dept = department_crud.get_by_code(db, dept_code=dept_code)
            if not dept:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="部门不存在"
                )
            
            result = self.crud.get_by_dept_id(
                db,
                dept_code=dept_code,
                page=params.get("page", 1),
                page_size=params.get("page_size", 10),
                name=params.get("name")
            )
            
            # 转换为响应模型
            result["items"] = [self._to_response_model(item) for item in result["items"]]
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            log.error(f"获取部门人员列表失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取部门人员列表失败，请稍后重试"
            )
    
    def import_personnel(self, db: Session, file_content: bytes) -> PersonnelImportResult:
        """导入人员信息"""
        try:
            # 读取Excel文件
            df = pd.read_excel(BytesIO(file_content))
            
            # 定义必需的列
            required_columns = ['姓名', '工号', '身份证号']
            
            # 检查列是否存在
            for col in required_columns:
                if col not in df.columns:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"文件缺少必需的列: {col}"
                    )
            
            success_count = 0
            failed_count = 0
            failed_details = []
            
            # 逐行处理数据
            for index, row in df.iterrows():
                try:
                    # 构建人员数据
                    personnel_data = PersonnelCreate(
                        name=str(row['姓名']).strip() if pd.notna(row['姓名']) else '',
                        certificate_number=str(row['工号']).strip() if pd.notna(row['工号']) else '',
                        id_card_number=str(row['身份证号']).strip() if pd.notna(row['身份证号']) else '',
                        department_id=int(row['部门ID']) if '部门ID' in df.columns and pd.notna(row['部门ID']) else None,
                        position=str(row['职务']).strip() if '职务' in df.columns and pd.notna(row['职务']) else None,
                        rank=str(row['职级']).strip() if '职级' in df.columns and pd.notna(row['职级']) else None,
                        hire_date=pd.to_datetime(row['入职日期']).date() if '入职日期' in df.columns and pd.notna(row['入职日期']) else None
                    )
                    
                    # 调用创建方法
                    self.create_personnel(db, personnel_data)
                    success_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    failed_details.append({
                        "row": index + 2,  # Excel行号从1开始，加上标题行
                        "error": str(e)
                    })
            
            return PersonnelImportResult(
                success_count=success_count,
                failed_count=failed_count,
                failed_details=failed_details
            )
            
        except HTTPException:
            raise
        except Exception as e:
            log.error(f"导入人员失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件格式不正确或处理失败: {str(e)}"
            )
    
    def export_personnel(self, db: Session, params: Dict[str, Any]) -> bytes:
        """导出人员信息"""
        try:
            # 获取导出数据
            personnel_list = self.crud.get_for_export(
                db,
                dept_code=params.get("department_id"),
                start_date=params.get("start_date"),
                end_date=params.get("end_date")
            )
            
            # 构建导出数据
            export_data = []
            for p in personnel_list:
                export_data.append({
                    "姓名": p.name,
                    "工号": p.certificate_number,
                    "身份证号": p.id_card_number,
                    "部门": p.department.full_name if p.department else "",
                    "职务": p.position or "",
                    "职级": p.rank or "",
                    "入职日期": p.hire_date.strftime("%Y-%m-%d") if p.hire_date else ""
                })
            
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 写入Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='人员信息')
            output.seek(0)
            
            return output.getvalue()
            
        except Exception as e:
            log.error(f"导出人员失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="导出人员失败，请稍后重试"
            )
    
    def _to_response_model(self, db_personnel: Any) -> PersonnelResponse:
        """将数据库模型转换为响应模型"""
        # 安全处理department可能为None的情况
        department_name = None
        if db_personnel and hasattr(db_personnel, 'department') and db_personnel.department:
            department_name = db_personnel.department.full_name if hasattr(db_personnel.department, 'full_name') else None
        
        return PersonnelResponse(
            id=db_personnel.id,
            name=db_personnel.name,
            certificate_number=db_personnel.certificate_number,
            id_card_number=db_personnel.id_card_number,
            dept_code=db_personnel.dept_code,
            department_name=department_name,
            position=db_personnel.position,
            rank=db_personnel.rank,
            hire_date=db_personnel.hire_date,
            create_time=db_personnel.create_time,
            update_time=db_personnel.update_time
        )


# 创建服务实例
personnel_service = PersonnelService()
