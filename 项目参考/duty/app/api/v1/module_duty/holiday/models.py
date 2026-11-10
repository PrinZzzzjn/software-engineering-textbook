# 节假日模型 - 避免循环导入
from sqlalchemy import Column, String, Date, Boolean, Index, Integer
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy import Enum as SQLEnum
import enum
from app.core.base_model import BaseModel

# 定义枚举值
HOLIDAY_TYPE_ENUM = ["01", "02", "03"]

class HolidayType(enum.Enum):
    """节假日类型枚举"""
    LEGAL_HOLIDAY = "01"
    WEEKEND = "02"
    SPECIAL_HOLIDAY = "03"


class Holiday(BaseModel):
    """节假日模型"""
    __tablename__ = "holidays"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    is_holiday = Column(Boolean, nullable=False, default=True)
    # 使用字符串枚举，直接接受字符串值
    holiday_type = Column(String(50), nullable=True)
    name = Column(String(100), nullable=True)
    description = Column(String(255), nullable=True)
