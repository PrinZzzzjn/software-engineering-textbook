from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.core.dependencies import get_current_user, get_current_admin_user
from app.api.v1.module_duty.duty_record.service import DutyRecordService
from app.api.v1.module_duty.duty_record.schema import (
    DutyRecordCreate,
    DutyRecordUpdate,
    DutyRecordResponse,
    DutyRecordDetailResponse,
    DutyRecordListResponse
)
from app.api.v1.module_duty.duty_record.param import DutyRecordQueryParams
# 移除不必要的User导入

# 创建路由器
router = APIRouter(prefix="/duty-records", tags=["值班记录管理"])

@router.get("", response_model=DutyRecordListResponse,summary="获取值班记录列表")
def get_duty_records(
    params: DutyRecordQueryParams = Depends(),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取值班记录列表
    
    Args:
        params: 查询参数，包含分页、筛选条件等
        current_user: 当前登录用户
        
    Returns:
        包含值班记录列表的分页响应
    """
    try:
        service = DutyRecordService()
        result = service.get_duty_record_list(
            page=params.page,
            page_size=params.page_size,
            start_time=params.start_time,
            end_time=params.end_time,
            personnel_certificate_number=params.personnel_certificate_number,
            workstation_id=params.workstation_id,
            status=params.status,
            sort_by=params.sort_by,
            sort_order=params.sort_order
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("", response_model=DutyRecordDetailResponse, status_code=status.HTTP_201_CREATED,summary="创建值班记录（仅管理员）")
def create_duty_record(
    duty_record_data: DutyRecordCreate,
    current_user: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """创建值班记录（仅管理员）
    
    Args:
        duty_record_data: 值班记录创建数据
        current_user: 当前登录用户（必须是管理员）
        
    Returns:
        创建的值班记录详情
    """
    try:
        # 设置创建人为当前用户ID
        duty_record_data.created_by = current_user['id']
        
        service = DutyRecordService()
        result = service.create_duty_record(duty_record_data)
        return result
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{id}", response_model=DutyRecordDetailResponse,summary="获取单个值班记录详情")
def get_duty_record(
    id: int,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取单个值班记录详情
    
    Args:
        id: 值班记录ID
        current_user: 当前登录用户
        
    Returns:
        值班记录详情
    """
    try:
        service = DutyRecordService()
        result = service.get_duty_record_by_id(id)
        return result
    except Exception as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{id}", response_model=DutyRecordDetailResponse,summary="更新值班记录（仅管理员）")
def update_duty_record(
    id: int,
    duty_record_data: DutyRecordUpdate,
    current_user: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """更新值班记录（仅管理员）
    
    Args:
        id: 值班记录ID
        duty_record_data: 值班记录更新数据
        current_user: 当前登录用户（必须是管理员）
        
    Returns:
        更新后的值班记录详情
    """
    try:
        service = DutyRecordService()
        result = service.update_duty_record(id, duty_record_data)
        return result
    except Exception as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{id}", response_model=Dict[str, str],summary="删除值班记录（仅管理员）")
def delete_duty_record(
    id: int,
    current_user: dict = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """删除值班记录（仅管理员）
    
    Args:
        id: 值班记录ID
        current_user: 当前登录用户（必须是管理员）
        
    Returns:
        删除结果消息
    """
    try:
        service = DutyRecordService()
        result = service.delete_duty_record(id)
        return result
    except Exception as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/statistics/summary",summary="获取值班统计信息")
def get_duty_statistics(
    start_time: str = None,
    end_time: str = None,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取值班统计信息
    
    Args:
        start_time: 开始时间（可选）
        end_time: 结束时间（可选）
        current_user: 当前登录用户
        
    Returns:
        值班统计数据
    """
    try:
        # 转换时间字符串为datetime对象
        from datetime import datetime
        start_datetime = datetime.fromisoformat(start_time) if start_time else None
        end_datetime = datetime.fromisoformat(end_time) if end_time else None
        
        service = DutyRecordService()
        result = service.get_duty_statistics(start_datetime, end_datetime)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"时间格式错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
