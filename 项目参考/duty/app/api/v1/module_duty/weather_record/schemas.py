from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.core.base_schema import BaseSchema

# 天气记录基础模型
class WeatherRecordBase(BaseSchema):
    """天气记录基础模型"""
    record_time: datetime = Field(..., description="记录时间（精确到小时）")
    dept_code: str = Field(..., description="部门代码")
    temperature: float = Field(..., description="气温(摄氏度)")
    humidity: float = Field(..., description="相对湿度(%)")
    rainfall: float = Field(default=0, description="降雨量(mm)")
    snowfall: float = Field(default=0, description="降雪量(cm)")
    wind_speed: float = Field(default=0, description="风速(m/s)")

# 天气记录创建请求模型
class WeatherRecordCreate(WeatherRecordBase):
    """创建天气记录请求模型"""
    pass

# 天气记录更新请求模型
class WeatherRecordUpdate(BaseSchema):
    """更新天气记录请求模型"""
    dept_code: Optional[str] = Field(default=None, description="部门代码")
    temperature: Optional[float] = Field(default=None, description="气温(摄氏度)")
    humidity: Optional[float] = Field(default=None, description="相对湿度(%)")
    rainfall: Optional[float] = Field(default=None, description="降雨量(mm)")
    snowfall: Optional[float] = Field(default=None, description="降雪量(cm)")
    wind_speed: Optional[float] = Field(default=None, description="风速(m/s)")

# 天气记录响应模型
class WeatherRecordResponse(BaseSchema):
    """天气记录响应模型"""
    id: int = Field(..., description="记录ID")
    record_time: datetime = Field(..., description="记录时间（精确到小时）")
    dept_code: str = Field(..., description="部门代码")
    temperature: float = Field(..., description="气温(摄氏度)")
    humidity: float = Field(..., description="相对湿度(%)")
    rainfall: float = Field(default=0, description="降雨量(mm)")
    snowfall: float = Field(default=0, description="降雪量(cm)")
    wind_speed: float = Field(default=0, description="风速(m/s)")
    weather_conditions: List[str] = Field(..., description="天气状况数组")

# 导入失败记录模型
class ImportFailedRecord(BaseSchema):
    """导入失败记录"""
    row: int = Field(..., description="失败行号")
    error: str = Field(..., description="错误信息")

# 批量导入响应模型
class ImportResponse(BaseSchema):
    """批量导入响应模型"""
    message: str = Field(..., description="导入结果消息")
    success_count: int = Field(..., description="成功导入数量")
    failed_count: int = Field(..., description="失败导入数量")
    failed_records: List[ImportFailedRecord] = Field(default_factory=list, description="失败记录详情")
