from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime
from app.core.dependencies import get_current_user, get_current_admin_user
from app.api.v1.module_duty.inspection_record.service import InspectionRecordService
from app.api.v1.module_duty.inspection_record.schema import (
    InspectionRecordCreate,
    InspectionRecordUpdate,
    InspectionRecordResponse,
    InspectionRecordDetailResponse,
    InspectionRecordListResponse
)
from app.api.v1.module_duty.inspection_record.param import InspectionRecordQueryParams

# 创建路由器
router = APIRouter(prefix="/inspection-records", tags=["查班记录管理"])

@router.get("", response_model=InspectionRecordListResponse,summary="获取查班记录列表")
def get_inspection_records(
    params: InspectionRecordQueryParams = Depends(),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取查班记录列表
    
    Args:
        params: 查询参数，包含分页、筛选条件等
        current_user: 当前登录用户
        
    Returns:
        包含查班记录列表的分页响应
    """
    try:
        service = InspectionRecordService()
        result = service.get_inspection_record_list(
            page=params.page,
            page_size=params.page_size,
            start_date=params.start_date,
            end_date=params.end_date,
            inspector_certificate_number=params.inspector_certificate_number,
            duty_record_id=params.duty_record_id,
            inspection_type=params.inspection_type,
            evaluation_level=params.evaluation_level,
            sort_by=params.sort_by,
            sort_order=params.sort_order
        )
        return result
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("", response_model=InspectionRecordResponse, status_code=status.HTTP_201_CREATED,summary="创建查班记录")
def create_inspection_record(
    inspection_record_data: InspectionRecordCreate,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """创建查班记录
    
    Args:
        inspection_record_data: 查班记录创建数据
        current_user: 当前登录用户
        
    Returns:
        创建的查班记录
    """
    try:
        service = InspectionRecordService()
        result = service.create_inspection_record(inspection_record_data, current_user['id'])
        return result
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        if "值班记录不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="值班记录不存在"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{id}", response_model=InspectionRecordDetailResponse,summary="获取单个查班记录详情")
def get_inspection_record(
    id: int,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取单个查班记录详情
    
    Args:
        id: 查班记录ID
        current_user: 当前登录用户
        
    Returns:
        查班记录详情
    """
    try:
        service = InspectionRecordService()
        result = service.get_inspection_record_by_id(id)
        return result
    except Exception as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="查班记录不存在"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{id}", response_model=InspectionRecordResponse,summary="更新查班记录（仅管理员或创建者）")
def update_inspection_record(
    id: int,
    inspection_record_data: InspectionRecordUpdate,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """更新查班记录（仅管理员或创建者）
    
    Args:
        id: 查班记录ID
        inspection_record_data: 查班记录更新数据
        current_user: 当前登录用户
        
    Returns:
        更新后的查班记录
    """
    try:
        # 获取记录以检查权限
        service = InspectionRecordService()
        record = service.get_inspection_record_by_id(id)
        
        # 检查权限：只有管理员或记录创建者可以修改
        if current_user.get('role') != 'ADMIN' and record.get('inspector_certificate_number') != current_user.get('certificate_number'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        # 执行更新
        result = service.update_inspection_record(id, inspection_record_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="查班记录不存在"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{id}", response_model=Dict[str, str],summary="删除查班记录（仅管理员）")
def delete_inspection_record(
    id: int,
    current_user: dict = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """删除查班记录（仅管理员）
    
    Args:
        id: 查班记录ID
        current_user: 当前登录用户（必须是管理员）
        
    Returns:
        删除结果消息
    """
    try:
        service = InspectionRecordService()
        result = service.delete_inspection_record(id)
        return result
    except Exception as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="查班记录不存在"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/statistics/summary", response_model=Dict[str, Any],summary="获取查班统计信息")
def get_inspection_statistics(
    start_date: str = None,
    end_date: str = None,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取查班统计信息
    
    Args:
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        current_user: 当前登录用户
        
    Returns:
        查班统计数据
    """
    try:
        # 转换时间字符串为datetime对象
        start_datetime = datetime.fromisoformat(start_date) if start_date else None
        end_datetime = datetime.fromisoformat(end_date) if end_date else None
        
        service = InspectionRecordService()
        result = service.get_inspection_statistics(start_datetime, end_datetime)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"时间格式错误: {str(e)}"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )