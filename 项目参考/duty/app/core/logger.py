from loguru import logger
import os
from app.config.setting import settings

# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

# 清除默认的日志处理器
logger.remove()

# 配置控制台日志
logger.add(
    sink=lambda msg: print(msg, end=""),  # 控制台输出
    level="DEBUG" if settings.DEBUG else "INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    enqueue=True,  # 异步处理
    backtrace=True,  # 完整的异常回溯
    diagnose=True,  # 显示变量值（开发环境）
)

# 配置文件日志 - 错误日志
logger.add(
    sink=os.path.join(LOG_DIR, "error.log"),
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message}",
    rotation="100 MB",  # 文件大小超过100MB时轮转
    retention="30 days",  # 保留30天的日志
    compression="zip",  # 压缩旧日志
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

# 配置文件日志 - 所有日志
logger.add(
    sink=os.path.join(LOG_DIR, "app.log"),
    level="DEBUG" if settings.DEBUG else "INFO",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message}",
    rotation="100 MB",
    retention="14 days",
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

# 配置SQL日志（仅在调试模式下）
if settings.DEBUG:
    logger.add(
        sink=os.path.join(LOG_DIR, "sql.log"),
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | SQL | {message}",
        rotation="50 MB",
        retention="7 days",
        enqueue=True,
    )

# 导出logger实例供其他模块使用
log = logger