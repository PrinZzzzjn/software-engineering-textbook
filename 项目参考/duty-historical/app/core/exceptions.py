from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from typing import Optional, Dict, Any

# 自定义异常类
class BaseAppException(Exception):
    """应用基础异常类"""
    def __init__(self,
                 status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
                 detail: Any = "Internal server error",
                 headers: Optional[Dict[str, Any]] = None):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

class NotFoundException(BaseAppException):
    """资源未找到异常"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class BadRequestException(BaseAppException):
    """请求参数错误异常"""
    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class UnauthorizedException(BaseAppException):
    """未授权异常"""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class ForbiddenException(BaseAppException):
    """禁止访问异常"""
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class DuplicateResourceException(BaseAppException):
    """资源重复异常"""
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )

# 统一异常处理函数
async def app_exception_handler(request: Request, exc: BaseAppException):
    """处理应用自定义异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "error": exc.__class__.__name__
        },
        headers=exc.headers
    )

# FastAPI标准异常处理
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理FastAPI HTTP异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "error": "HTTPException"
        },
        headers=exc.headers
    )

# 通用异常处理
async def generic_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Internal server error",
            "error": exc.__class__.__name__
        }
    )