# 人员管理模块初始化文件
from fastapi import APIRouter
from app.api.v1.module_duty.personnel.controller import router as personnel_router

# 创建主路由器
router = APIRouter()

# 包含人员管理路由
router.include_router(personnel_router)

# 导出路由
__all__ = ["router"]