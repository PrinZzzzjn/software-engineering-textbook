from typing import Any, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.core.base_schema import PaginatedResponse
from app.api.v1.module_duty.equipment_cabinet_record.schema import (
    EquipmentCabinetRecordCreate, EquipmentCabinetRecordUpdate, EquipmentCabinetRecordResponse,
    EquipmentCabinetRecordDetailResponse, EquipmentCabinetRecordListItem, EnumListResponse
)
from app.api.v1.module_duty.equipment_cabinet_record.param import EquipmentCabinetRecordQueryParams
from app.api.v1.module_duty.equipment_cabinet_record.service import equipment_cabinet_record_service

router = APIRouter(prefix="/equipment-cabinet-records", tags=["设备柜记录管理"])

@router.get("/", response_model=PaginatedResponse[EquipmentCabinetRecordListItem],summary="获取设备柜记录列表")
def get_equipment_cabinet_records(
    params: EquipmentCabinetRecordQueryParams = Depends(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取设备柜记录列表"""
    try:
        result = equipment_cabinet_record_service.get_equipment_cabinet_record_list(db, params=params)
        
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
                
                # 获取枚举值
                open_reason_type_value = record.open_reason_type.value if hasattr(record.open_reason_type, 'value') else record.open_reason_type
                open_type_value = record.open_type.value if hasattr(record.open_type, 'value') else record.open_type
                open_result_value = record.open_result.value if hasattr(record.open_result, 'value') else record.open_result
                
                item = EquipmentCabinetRecordListItem(
                    id=record.id,
                    dept_code=record.dept_code,
                    dept_name=dept_name,
                    device_id=record.device_id,
                    applicant_certificate_number=record.applicant_certificate_number,
                    applicant_name=applicant_name,
                    authorizer_certificate_number=record.authorizer_certificate_number,
                    authorizer_name=authorizer_name,
                    application_time=record.application_time,
                    open_reason_type=open_reason_type_value,
                    open_type=open_type_value,
                    open_result=open_result_value,
                    cabinet_open_time=record.cabinet_open_time,
                    cabinet_close_time=record.cabinet_close_time,
                    device_quantity_change=record.device_quantity_change,
                    create_time=record.create_time,
                    update_time=record.update_time
                )
                items.append(item)
            except AttributeError as e:
                from app.core.logger import logger
                logger.error(f"处理记录列表时发生属性错误: {str(e)}")
                # 跳过有问题的记录，继续处理其他记录
                continue
        
        # 计算总页数
        pages = (result["total"] + result["page_size"] - 1) // result["page_size"]
        
        return PaginatedResponse[EquipmentCabinetRecordListItem](
            items=items,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            pages=pages
        )
    except Exception as e:
        from app.core.logger import logger
        logger.error(f"获取设备柜记录列表时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取记录列表时发生错误: {str(e)}")

@router.post("/", response_model=EquipmentCabinetRecordResponse, status_code=status.HTTP_201_CREATED,summary="创建设备柜记录")
def create_equipment_cabinet_record(
    record_in: EquipmentCabinetRecordCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """创建设备柜记录"""
    # 创建设备柜记录
    record = equipment_cabinet_record_service.create_equipment_cabinet_record(db, record_in=record_in)
    
    # 确保正确返回所有字段，包括关闭时间
    return EquipmentCabinetRecordResponse(
        id=record.id,
        dept_code=record.dept_code,
        device_id=record.device_id,
        open_reason_type=record.open_reason_type.value,
        applicant_certificate_number=record.applicant_certificate_number,
        application_time=record.application_time,
        authorizer_certificate_number=record.authorizer_certificate_number,
        open_type=record.open_type.value,
        open_result=record.open_result.value,
        cabinet_open_time=record.cabinet_open_time,
        cabinet_close_time=record.cabinet_close_time,  # 确保返回关闭时间
        device_quantity_change=record.device_quantity_change,
        create_time=record.create_time,
        update_time=record.update_time
    )

@router.get("/{id}", response_model=EquipmentCabinetRecordDetailResponse,summary="获取单个设备柜记录详情")
def get_equipment_cabinet_record(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取单个设备柜记录详情"""
    detail = equipment_cabinet_record_service.get_equipment_cabinet_record_detail(db, id=id)
    return EquipmentCabinetRecordDetailResponse(**detail)

@router.put("/{id}", response_model=EquipmentCabinetRecordResponse,summary="更新设备柜记录")
def update_equipment_cabinet_record(
    id: int,
    record_in: EquipmentCabinetRecordUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """更新设备柜记录"""
    record = equipment_cabinet_record_service.update_equipment_cabinet_record(db, id=id, record_in=record_in)
    return EquipmentCabinetRecordResponse(
        id=record.id,
        dept_code=record.dept_code,
        device_id=record.device_id,
        open_reason_type=record.open_reason_type.value,
        applicant_certificate_number=record.applicant_certificate_number,
        application_time=record.application_time,
        authorizer_certificate_number=record.authorizer_certificate_number,
        open_type=record.open_type.value,
        open_result=record.open_result.value,
        cabinet_open_time=record.cabinet_open_time,
        cabinet_close_time=record.cabinet_close_time,
        device_quantity_change=record.device_quantity_change,
        create_time=record.create_time,
        update_time=record.update_time
    )

@router.delete("/{id}", response_model=Dict[str, str],summary="删除设备柜记录")
def delete_equipment_cabinet_record(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除设备柜记录"""
    equipment_cabinet_record_service.delete_equipment_cabinet_record(db, id=id)
    return {"message": "设备柜记录删除成功"}

@router.get("/open_reason_types", response_model=EnumListResponse,summary="获取开启原因类型列表")
def get_open_reason_types(
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取开启原因类型列表"""
    items = equipment_cabinet_record_service.get_open_reason_types()
    return EnumListResponse(items=items)

@router.get("/open_types", response_model=EnumListResponse,summary="获取开柜类型列表")
def get_open_types(
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取开柜类型列表"""
    items = equipment_cabinet_record_service.get_open_types()
    return EnumListResponse(items=items)

@router.get("/open_results", response_model=EnumListResponse,summary="获取开柜结果列表")
def get_open_results(
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取开柜结果列表"""
    items = equipment_cabinet_record_service.get_open_results()
    return EnumListResponse(items=items)