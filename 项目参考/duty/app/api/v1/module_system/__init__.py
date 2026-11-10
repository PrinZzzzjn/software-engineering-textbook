from fastapi import APIRouter
from app.api.v1.module_system.auth import router as auth_router
from app.api.v1.module_system.user import router as user_router

# 创建系统模块路由
router = APIRouter(prefix="")

# 包含认证模块路由
router.include_router(auth_router)

# 包含用户管理模块路由
router.include_router(user_router)
