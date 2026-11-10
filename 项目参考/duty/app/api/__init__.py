from fastapi import APIRouter
from app.api.v1 import v1_router

# 创建API路由
router = APIRouter(prefix="/api")

# 包含v1版本路由
router.include_router(v1_router)
