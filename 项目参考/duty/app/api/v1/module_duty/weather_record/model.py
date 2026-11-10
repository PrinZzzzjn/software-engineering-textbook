from sqlalchemy import Column, String, DateTime, Float, Index, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.core.base_model import BaseModel

class WeatherRecord(BaseModel):
    """天气记录模型（每小时）"""
    __tablename__ = "weather_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='记录ID')
    record_time = Column(DateTime(timezone=True), nullable=False, index=True, comment='记录时间（精确到小时）')
    dept_code = Column(String(50), ForeignKey('dept.dept_code'), nullable=False, comment='部门编码')
    temperature = Column(Float, nullable=False, comment='气温(摄氏度)')
    humidity = Column(Float, nullable=False, comment='相对湿度(%)')
    rainfall = Column(Float, default=0, comment='降雨量(mm)')
    snowfall = Column(Float, default=0, comment='降雪量(cm)')
    wind_speed = Column(Float, default=0, comment='风速(m/s)')
    weather_conditions = Column(String(500), default='[]', comment='天气状况描述(JSON格式)')

    # 关联关系
    department = relationship('Department', backref='weather_records')
    
    # 索引
    __table_args__ = (
        Index('idx_record_time', 'record_time'),
        Index('idx_dept_time', 'dept_code', 'record_time'),
    )
    
    @staticmethod
    def calculate_weather_conditions(temperature, humidity, rainfall, snowfall, wind_speed):
        """
        计算天气情况数组，基于天气标准.md中的标准
        返回字符串数组，包含气温状况、湿度状况、降雨状况、降雪状况、风速状况
        """
        conditions = []
        
        # 1. 气温状况判定
        if temperature <= -20:
            conditions.append("极寒")
        elif temperature <= -10:
            conditions.append("严寒")
        elif temperature <= 0:
            conditions.append("寒冷")
        elif temperature <= 14:
            conditions.append("清凉")
        elif temperature <= 25:
            conditions.append("舒适")
        elif temperature <= 32:
            conditions.append("温暖")
        elif temperature <= 39:
            conditions.append("炎热")
        else:
            conditions.append("酷热")
        
        # 2. 湿度状况判定
        if humidity <= 30:
            conditions.append("干燥")
        elif humidity <= 60:
            conditions.append("舒适湿度")
        elif humidity <= 80:
            conditions.append("潮湿")
        else:
            conditions.append("闷湿")
        
        # 3. 降雨状况判定
        if rainfall > 16.0:
            conditions.append("暴雨")
        elif rainfall > 8.0:
            conditions.append("大雨")
        elif rainfall > 2.5:
            conditions.append("中雨")
        elif rainfall > 0:
            conditions.append("小雨")
        
        # 4. 降雪状况判定 (注意：snowfall单位是cm，这里假设需要转换为mm/h进行判断)
        # 根据天气标准，降雪量是基于融化后的水量(mm/h)，这里简化处理
        snowfall_mm = snowfall * 10  # 粗略转换cm到mm
        if snowfall_mm > 4.0:
            conditions.append("暴雪")
        elif snowfall_mm > 1.5:
            conditions.append("大雪")
        elif snowfall_mm > 0.5:
            conditions.append("中雪")
        elif snowfall_mm > 0:
            conditions.append("小雪")
        
        # 5. 风速状况判定
        if wind_speed >= 13.9:
            conditions.append("烈风")
        elif wind_speed >= 10.8:
            conditions.append("大风")
        elif wind_speed >= 8.0:
            conditions.append("强风")
        elif wind_speed >= 5.5:
            conditions.append("清风")
        elif wind_speed >= 3.4:
            conditions.append("和风")
        else:
            conditions.append("无风/微风")
        
        return conditions
        
    @property
    def weather_conditions_array(self):
        """
        将存储的JSON字符串转换回数组格式
        为了向后兼容，保留此属性
        """
        import json
        try:
            return json.loads(self.weather_conditions)
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，使用新的静态方法计算
            return self.calculate_weather_conditions(
                self.temperature, self.humidity, self.rainfall, 
                self.snowfall, self.wind_speed
            )
