from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
from app.core.exceptions import (
    app_exception_handler, http_exception_handler, generic_exception_handler,
    BaseAppException
)
from app.config.setting import settings

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="值班数据统计服务API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# 包含API路由
app.include_router(api_router)

# 根路径
@app.get("/")
def read_root():
    """根路径"""
    return {
        "message": "Welcome to Duty System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# 健康检查
@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}
