from pydantic import BaseModel
from typing import List, Optional, Dict, Union
from datetime import datetime


class MonthlyDuty(BaseModel):
    """月度值班统计"""
    month: int
    days: int
    hours: int


class StaffDutyYearly(BaseModel):
    """人员年度值班统计响应模型"""
    personnel_certificate_number: str
    personnel_name: str
    year: str
    total_duty_days: int
    total_duty_hours: float
    duty_by_month: List[MonthlyDuty]


class HourDistribution(BaseModel):
    """小时分布统计"""
    hour: int
    count: int


class DutyTimeDistribution(BaseModel):
    """值班时间段分布响应模型"""
    year: str
    personnel_certificate_number: str
    personnel_name: str
    time_distribution: List[HourDistribution]
    peak_hours: List[int]
    total_records: int


class WorkstationDutyYearly(BaseModel):
    """工位年度值班统计响应模型"""
    workstation_id: str
    workstation_name: str
    year: str
    total_duty_days: int
    total_duty_hours: float
    duty_by_month: List[MonthlyDuty]


class ContributionRanking(BaseModel):
    """值班贡献度和排名响应模型"""
    personnel_certificate_number: str
    personnel_name: str
    year: str
    total_duty_hours: float
    dept_total_hour: float
    dept_average_hours: float
    contribution_rate: float
    contribution_percentage: str
    ranking: int
    total_staff_count: int
    dept_id: str
    dept_name: str


class HolidayDutyItem(BaseModel):
    """节假日值班记录项"""
    duty_id: str
    staff_certificate_number: str
    staff_name: str
    start_time: datetime
    end_time: datetime
    holiday_name: str
    site_name: str


class HolidayDutyStat(BaseModel):
    """节假日值班统计响应模型"""
    total: int
    page: int
    page_size: int
    year: str
    total_duty_records: int
    total_holiday_records: int
    total_holiday_duty_days: int
    total_holiday_duty_hours: float
    items: List[HolidayDutyItem]


class ExtremeWeatherDutyRecord(BaseModel):
    """极端天气值班记录项"""
    duty_id: str
    duty_date: datetime


class WeatherTypeSummary(BaseModel):
    """天气类型汇总"""
    type: str
    count: int


class WeatherExtremeValue(BaseModel):
    """天气极值记录"""
    value: float
    record_time: datetime
    duty_id: Optional[Union[str, int]] = None


class WeatherExtremeStats(BaseModel):
    """天气极值统计响应模型"""
    personnel_certificate_number: str
    personnel_name: str
    year: str
    max_temperature: WeatherExtremeValue
    min_temperature: WeatherExtremeValue
    max_rainfall: WeatherExtremeValue
    max_snowfall: WeatherExtremeValue
    max_wind_speed: WeatherExtremeValue
    total_duty_days: int
    total_duty_hours: float


class ExtremeWeatherDutyStat(BaseModel):
    """极端天气值班统计响应模型"""
    personnel_id: str
    personnel_name: str
    year: str
    total_duty_days: int
    total_duty_hours: float
    total_duty_records: int
    extreme_duty_records: List[ExtremeWeatherDutyRecord]
    weather_type_summary: List[WeatherTypeSummary]
