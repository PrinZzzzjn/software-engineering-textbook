from fastapi import APIRouter
from app.api.v1.module_duty.safe_record.controller import router as safe_record_router

# 创建保险箱记录模块路由
router = APIRouter(prefix="/safe-records", tags=["保险箱记录管理"])

# 包含保险箱记录控制器的路由
router.include_router(safe_record_router)
