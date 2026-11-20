from fastapi import APIRouter
from app.api.v1.module_system import router as system_router
from app.api.v1.module_duty.dept import router as dept_router
from app.api.v1.module_duty.personnel import router as personnel_router
from app.api.v1.module_duty.workstation import router as workstation_router
from app.api.v1.module_duty.duty_record import router as duty_record_router
from app.api.v1.module_duty.inspection_record import router as inspection_record_router
from app.api.v1.module_duty.safe_record import router as safe_record_router
from app.api.v1.module_duty.equipment_cabinet_record import router as equipment_cabinet_record_router
from app.api.v1.module_duty.holiday import router as holiday_router
from app.api.v1.module_duty.analytics import router as analytics_router
from app.api.v1.module_duty.weather_record import router as weather_record_router

# 创建v1版本路由
v1_router = APIRouter(prefix="/v1")

# 包含系统模块路由
v1_router.include_router(system_router)

# 包含部门管理模块路由
v1_router.include_router(dept_router)

# 包含人员管理模块路由
v1_router.include_router(personnel_router)

# 包含工位管理模块路由
v1_router.include_router(workstation_router)

# 包含值班记录模块路由
v1_router.include_router(duty_record_router)

# 包含查班记录模块路由
v1_router.include_router(inspection_record_router)

# 包含保险箱记录模块路由
v1_router.include_router(safe_record_router)

# 包含设备柜记录模块路由
v1_router.include_router(equipment_cabinet_record_router)

# 包含节假日管理模块路由
v1_router.include_router(holiday_router)

# 包含数据分析模块路由
v1_router.include_router(analytics_router)

# 包含天气记录模块路由
v1_router.include_router(weather_record_router)

__all__ = ["v1_router"]
