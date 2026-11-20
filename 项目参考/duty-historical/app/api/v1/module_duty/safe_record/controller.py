from typing import Any, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.core.base_schema import PaginatedResponse
from app.api.v1.module_duty.safe_record.schema import (
    SafeBoxRecordCreate, SafeBoxRecordUpdate, SafeBoxRecordResponse,
    SafeBoxRecordDetailResponse, SafeBoxRecordListItem, EnumListResponse
)
from app.api.v1.module_duty.safe_record.param import SafeBoxRecordQueryParams
from app.api.v1.module_duty.safe_record.service import safe_box_record_service

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[SafeBoxRecordListItem],summary="获取保险箱记录列表")
def get_safe_box_records(
    params: SafeBoxRecordQueryParams = Depends(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取保险箱记录列表"""
    try:
        result = safe_box_record_service.get_safe_box_record_list(db, params=params)
        
        # 转换为响应模型
        items = []
        for record in result["items"]:
            try:
                # 安全获取关联对象属性
                dept_name = ""
                if hasattr(record, 'department') and record.department and hasattr(record.department, 'full_name'):
                    dept_name = record.department.full_name
                
                applicant_name = ""
                if hasattr(record, 'applicant') and record.applicant and hasattr(record.applicant, 'full_name'):
                    applicant_name = record.applicant.full_name
                
                authorizer_name = ""
                if hasattr(record, 'authorizer') and record.authorizer and hasattr(record.authorizer, 'full_name'):
                    authorizer_name = record.authorizer.full_name
                
                # 转换枚举值为名称
                try:
                    application_type_name = safe_box_record_service._get_enum_name(
                        type(record.application_type), record.application_type
                    )
                except Exception:
                    application_type_name = str(record.application_type)
                
                try:
                    authorization_type_name = safe_box_record_service._get_enum_name(
                        type(record.authorization_type), record.authorization_type
                    )
                except Exception:
                    authorization_type_name = str(record.authorization_type)
                
                try:
                    authorization_result_name = safe_box_record_service._get_enum_name(
                        type(record.authorization_result), record.authorization_result
                    )
                except Exception:
                    authorization_result_name = str(record.authorization_result)
                
                # 获取枚举值
                application_type_value = record.application_type.value if hasattr(record.application_type, 'value') else record.application_type
                authorization_type_value = record.authorization_type.value if hasattr(record.authorization_type, 'value') else record.authorization_type
                authorization_result_value = record.authorization_result.value if hasattr(record.authorization_result, 'value') else record.authorization_result
                
                item = SafeBoxRecordListItem(
                    id=record.id,
                    dept_code=record.dept_code,
                    dept_name=dept_name,
                    device_id=record.device_id,
                    applicant_certificate_number=record.applicant_certificate_number,
                    applicant_name=applicant_name,
                    application_time=record.application_time,
                    application_type=application_type_value,
                    application_type_name=application_type_name,
                    authorizer_certificate_number=record.authorizer_certificate_number,
                    authorizer_name=authorizer_name,
                    authorization_type=authorization_type_value,
                    authorization_type_name=authorization_type_name,
                    authorization_result=authorization_result_value,
                    authorization_result_name=authorization_result_name,
                    open_time=record.open_time,
                    close_time=record.close_time,
                    is_test_mode=record.is_test_mode,
                    created_at=record.create_time,
                    updated_at=record.update_time
                )
                items.append(item)
            except AttributeError as e:
                from app.core.logger import logger
                logger.error(f"AttributeError processing record in list: {str(e)}")
                logger.error(f"Record attributes: {dir(record)}")
                # 跳过有问题的记录，继续处理其他记录
                continue
        
        return PaginatedResponse[SafeBoxRecordListItem](
            items=items,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            pages=result["pages"]
        )
    except Exception as e:
        from app.core.logger import logger
        logger.error(f"Error in get_safe_box_records: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取记录列表时发生错误: {str(e)}")

@router.post("/", response_model=SafeBoxRecordResponse, status_code=status.HTTP_201_CREATED,summary="创建保险箱记录")
def create_safe_box_record(
    record_in: SafeBoxRecordCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """创建保险箱记录"""
    record = safe_box_record_service.create_safe_box_record(db, record_in=record_in)
    return SafeBoxRecordResponse(
        id=record.id,
        dept_code=record.dept_code,
        device_id=record.device_id,
        applicant_certificate_number=record.applicant_certificate_number,
        application_time=record.application_time,
        application_type=record.application_type.value,
        authorizer_certificate_number=record.authorizer_certificate_number,
        authorization_type=record.authorization_type.value,
        authorization_result=record.authorization_result.value,
        open_time=record.open_time,
        close_time=record.close_time,
        is_test_mode=record.is_test_mode,
        created_at=record.create_time,
        updated_at=record.update_time
    )

@router.get("/{id}", response_model=SafeBoxRecordDetailResponse,summary="获取单个保险箱记录详情")
def get_safe_box_record(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取单个保险箱记录详情"""
    detail = safe_box_record_service.get_safe_box_record_detail(db, id=id)
    return SafeBoxRecordDetailResponse(**detail)

@router.put("/{id}", response_model=SafeBoxRecordResponse,summary="更新保险箱记录")
def update_safe_box_record(
    id: int,
    record_in: SafeBoxRecordUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """更新保险箱记录"""
    record = safe_box_record_service.update_safe_box_record(db, id=id, record_in=record_in)
    return SafeBoxRecordResponse(
        id=record.id,
        dept_code=record.dept_code,
        device_id=record.device_id,
        applicant_certificate_number=record.applicant_certificate_number,
        application_time=record.application_time,
        application_type=record.application_type.value,
        authorizer_certificate_number=record.authorizer_certificate_number,
        authorization_type=record.authorization_type.value,
        authorization_result=record.authorization_result.value,
        open_time=record.open_time,
        close_time=record.close_time,
        is_test_mode=record.is_test_mode,
        created_at=record.create_time,
        updated_at=record.update_time
    )

@router.delete("/{id}", response_model=Dict[str, str],summary="删除保险箱记录")
def delete_safe_box_record(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除保险箱记录"""
    safe_box_record_service.delete_safe_box_record(db, id=id)
    return {"message": "保险箱记录删除成功"}

@router.get("/application_types", response_model=EnumListResponse,summary="获取申请类型列表")
def get_application_types(
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取申请类型列表"""
    items = safe_box_record_service.get_application_types()
    return EnumListResponse(items=items)

@router.get("/authorization_types", response_model=EnumListResponse,summary="获取授权类型列表")
def get_authorization_types(
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取授权类型列表"""
    items = safe_box_record_service.get_authorization_types()
    return EnumListResponse(items=items)

@router.get("/authorization_results", response_model=EnumListResponse,summary="获取授权结果列表")
def get_authorization_results(
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取授权结果列表"""
    items = safe_box_record_service.get_authorization_results()
    return EnumListResponse(items=items)
