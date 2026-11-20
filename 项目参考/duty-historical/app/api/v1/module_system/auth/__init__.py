from fastapi import APIRouter
from app.api.v1.module_system.auth.controller import router as auth_router

# 创建认证模块路由
router = APIRouter(prefix="/auth", tags=["认证"])

# 包含认证控制器的路由
router.include_router(auth_router)
