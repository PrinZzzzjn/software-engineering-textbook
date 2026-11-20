from fastapi import APIRouter
from app.api.v1.module_duty.dept.controller import router as dept_router

# 创建部门模块路由
router = APIRouter(prefix="/departments", tags=["部门管理"])

# 包含部门控制器的路由
router.include_router(dept_router)