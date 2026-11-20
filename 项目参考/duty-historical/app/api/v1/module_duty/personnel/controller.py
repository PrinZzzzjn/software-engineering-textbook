from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_active_user, get_current_admin_user
from app.api.v1.module_duty.personnel.schema import (
    PersonnelCreate, PersonnelUpdate, PersonnelResponse, PersonnelListResponse,
    PersonnelImportResult
)
from app.api.v1.module_duty.personnel.param import PersonnelQueryParams, PersonnelExportParams
from app.api.v1.module_duty.personnel.service import personnel_service
import io

# 创建路由器
router = APIRouter(prefix="/personnel", tags=["人员管理"])


@router.get("", response_model=PersonnelListResponse,summary="获取人员列表")
def get_personnel_list(
    params: PersonnelQueryParams = Depends(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """获取人员列表，支持分页、搜索和排序"""
    result = personnel_service.get_personnel_list(db, params.model_dump())
    return PersonnelListResponse(**result)


@router.post("", response_model=PersonnelResponse, status_code=status.HTTP_201_CREATED,summary="创建新人员信息（仅管理员）")
def create_personnel(
    personnel: PersonnelCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """创建新人员信息（仅管理员）"""
    return personnel_service.create_personnel(db, personnel)


@router.get("/{certificate_number}", response_model=PersonnelResponse,summary="获取指定人员的详细信息")
def get_personnel(
    certificate_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """获取指定人员的详细信息"""
    return personnel_service.get_personnel(db, certificate_number)


@router.put("/{certificate_number}", response_model=PersonnelResponse,summary="更新指定人员的信息（仅管理员）")
def update_personnel(
    certificate_number: str,
    personnel: PersonnelUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """更新指定人员的信息（仅管理员）"""
    return personnel_service.update_personnel(db, certificate_number, personnel)


@router.delete("/{certificate_number}", response_model=Dict[str, str],summary="删除指定人员（仅管理员）")
def delete_personnel(
    certificate_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """删除指定人员（仅管理员）"""
    return personnel_service.delete_personnel(db, certificate_number)


@router.post("/import", response_model=PersonnelImportResult,summary="批量导入人员信息（仅管理员）")
async def import_personnel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """批量导入人员信息（仅管理员）"""
    # 检查文件类型
    if not file.filename.endswith((".xls", ".xlsx")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件格式不正确，请上传Excel文件"
        )
    
    # 读取文件内容
    content = await file.read()
    
    return personnel_service.import_personnel(db, content)


@router.get("/export", response_model=PersonnelExportParams,summary="导出人员信息")
def export_personnel(
    dept_code: int = Query(None, description="部门编码筛选"),
    start_date: str = Query(None, description="入职开始日期（格式：YYYY-MM-DD）"),
    end_date: str = Query(None, description="入职结束日期（格式：YYYY-MM-DD）"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """导出人员信息"""
    # 构建参数
    params = {"dept_code": dept_code}
    
    # 转换日期格式
    if start_date:
        from datetime import datetime
        try:
            params["start_date"] = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始日期格式错误，请使用YYYY-MM-DD格式"
            )
    
    if end_date:
        from datetime import datetime
        try:
            params["end_date"] = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期格式错误，请使用YYYY-MM-DD格式"
            )
    
    # 导出数据
    excel_data = personnel_service.export_personnel(db, params)
    
    # 返回文件流
    return StreamingResponse(
        io.BytesIO(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=personnel_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )
