from fastapi import APIRouter
from app.api.v1.module_system.user.controller import router as user_router

# 创建用户模块路由
router = APIRouter(prefix="/users", tags=["用户管理"])

# 包含用户控制器的路由
router.include_router(user_router)
