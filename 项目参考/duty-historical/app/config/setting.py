from pydantic_settings import BaseSettings
from typing import Optional
import os
from pydantic import ConfigDict

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "值班数据统计服务"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./duty.db"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT配置
    SECRET_KEY: str = "test-secret-key-for-duty-system"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 使用Pydantic V2推荐的ConfigDict
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra='ignore'  # 忽略未定义的环境变量
    )

# 创建全局配置实例
settings = Settings()