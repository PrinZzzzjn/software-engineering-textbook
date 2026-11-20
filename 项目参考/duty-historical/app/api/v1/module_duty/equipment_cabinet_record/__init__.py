from fastapi import APIRouter
from app.api.v1.module_duty.equipment_cabinet_record import controller

router = APIRouter()
router.include_router(controller.router, tags=["设备柜记录管理"])
