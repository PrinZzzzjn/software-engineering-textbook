from fastapi import APIRouter
from app.api.v1.module_duty.dept import router as dept_router
from app.api.v1.module_duty.personnel import router as personnel_router
from app.api.v1.module_duty.workstation import router as workstation_router
from app.api.v1.module_duty.duty_record import router as duty_record_router
from app.api.v1.module_duty.inspection_record import router as inspection_record_router
from app.api.v1.module_duty.equipment_cabinet_record import router as equipment_cabinet_record_router
from app.api.v1.module_duty.holiday import router as holiday_router
from app.api.v1.module_duty.safe_record import router as safe_record_router

# 创建模块主路由器
router = APIRouter(prefix="/module-duty")

# 注册子模块路由
router.include_router(dept_router, tags=["部门管理"])
router.include_router(personnel_router, tags=["人员管理"])
router.include_router(workstation_router, tags=["工作站管理"])
router.include_router(duty_record_router, tags=["值班记录管理"])
router.include_router(inspection_record_router, tags=["查班记录管理"])
router.include_router(equipment_cabinet_record_router, tags=["设备柜记录管理"])
router.include_router(holiday_router, tags=["节假日管理"])
router.include_router(safe_record_router, tags=["保险箱记录管理"])

__all__ = ["router"]
