from fastapi import APIRouter
from .controller import router as analytics_router

router = APIRouter()
router.include_router(analytics_router, prefix="/analytics", tags=["数据分析"])
