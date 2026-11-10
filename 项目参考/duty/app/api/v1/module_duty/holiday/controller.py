# 重新设计的节假日控制器文件
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user, get_current_admin_user
from app.api.v1.module_duty.holiday.schemas import (
    Holiday, HolidayCreate, HolidayUpdate, HolidayListResponse,
    HolidayCheckResponse, ImportResult
)
from app.api.v1.module_duty.holiday.service import holiday_service

# 创建路由器
router = APIRouter(prefix="/holidays", tags=["节假日管理"])


@router.get("", response_model=HolidayListResponse, summary="获取节假日列表")
def get_holiday_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    start_date: str = Query(None, description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    is_holiday: bool = Query(None, description="是否为节假日"),
    holiday_type: str = Query(None, description="节假日类型"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取节假日列表（支持分页和筛选）"""
    try:
        # 转换日期格式
        start_date_obj = None
        end_date_obj = None
        if start_date:
            from datetime import datetime
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            from datetime import datetime
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # 获取节假日列表
        result = holiday_service.get_holiday_list(
            db=db,
            page=page,
            page_size=page_size,
            start_date=start_date_obj,
            end_date=end_date_obj,
            is_holiday=is_holiday,
            holiday_type=holiday_type
        )
        
        # 转换为响应模型
        items = []
        for holiday in result["items"]:
            item = Holiday(
                id=holiday.id,
                date=holiday.date,
                is_holiday=holiday.is_holiday,
                holiday_type=holiday.holiday_type if holiday.holiday_type else None,
                name=holiday.name,
                description=holiday.description,
                created_at=holiday.create_time,
                updated_at=holiday.update_time
            )
            items.append(item)
        
        return HolidayListResponse(
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            items=items
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取节假日列表失败: {str(e)}")


@router.post("", response_model=Holiday, status_code=status.HTTP_201_CREATED, summary="创建节假日")
def create_holiday(
    holiday_in: HolidayCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Any:
    """创建节假日（仅管理员）"""
    try:
        holiday = holiday_service.create_holiday(db, holiday_data=holiday_in)
        return Holiday(
            id=holiday.id,
            date=holiday.date,
            is_holiday=holiday.is_holiday,
            holiday_type=holiday.holiday_type if holiday.holiday_type else None,
            name=holiday.name,
            description=holiday.description,
            created_at=holiday.create_time,
            updated_at=holiday.update_time
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建节假日失败: {str(e)}")


@router.get("/{holiday_id}", response_model=Holiday, summary="获取节假日详情")
def get_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """获取节假日详情"""
    holiday = holiday_service.get_holiday_by_id(db, holiday_id)
    if not holiday:
        raise HTTPException(status_code=404, detail="节假日不存在")
    return Holiday(
        id=holiday.id,
        date=holiday.date,
        is_holiday=holiday.is_holiday,
        holiday_type=holiday.holiday_type if holiday.holiday_type else None,
        name=holiday.name,
        description=holiday.description,
        created_at=holiday.create_time,
                updated_at=holiday.update_time
    )


@router.put("/{holiday_id}", response_model=Holiday, summary="更新节假日")
def update_holiday(
    holiday_id: int,
    holiday_in: HolidayUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Any:
    """更新节假日（仅管理员）"""
    try:
        holiday = holiday_service.update_holiday(db, holiday_id, holiday_update=holiday_in)
        if not holiday:
            raise HTTPException(status_code=404, detail="节假日不存在")
        return Holiday(
            id=holiday.id,
            date=holiday.date,
            is_holiday=holiday.is_holiday,
            holiday_type=holiday.holiday_type if holiday.holiday_type else None,
            name=holiday.name,
            description=holiday.description,
            created_at=holiday.create_time,
            updated_at=holiday.update_time
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新节假日失败: {str(e)}")


@router.delete("/{holiday_id}", summary="删除节假日")
def delete_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> dict:
    """删除节假日（仅管理员）"""
    try:
        success = holiday_service.delete_holiday(db, holiday_id)
        if not success:
            raise HTTPException(status_code=404, detail="节假日不存在")
        return {"message": "节假日删除成功", "holiday_id": holiday_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除节假日失败: {str(e)}")


@router.get("/check/date", response_model=HolidayCheckResponse, summary="检查日期是否为节假日")
def check_holiday(
    date: str = Query(..., description="要检查的日期，格式：YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """检查指定日期是否为节假日"""
    try:
        return holiday_service.check_holiday(db, date_str=date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查节假日失败: {str(e)}")


@router.post("/import/excel", response_model=ImportResult, summary="从Excel导入节假日")
async def import_holidays(
    file: UploadFile = File(..., description="Excel文件"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Any:
    """从Excel文件批量导入节假日（仅管理员）"""
    try:
        # 验证文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="只支持Excel文件(.xlsx, .xls)")
        
        # 读取文件内容
        file_content = await file.read()
        
        # 导入节假日
        result = holiday_service.import_holidays_from_excel(db, file_content)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入节假日失败: {str(e)}")
