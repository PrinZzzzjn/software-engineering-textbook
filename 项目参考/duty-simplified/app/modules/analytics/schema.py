from pydantic import BaseModel


class MonthlyDuty(BaseModel):
    month: int
    days: int
    hours: float


class StaffDutyYearly(BaseModel):
    personnel_certificate_number: str
    year: str
    total_duty_days: int
    total_duty_hours: float
    duty_by_month: list[MonthlyDuty]


class HourDistribution(BaseModel):
    hour: int
    count: int


class DutyTimeDistribution(BaseModel):
    year: str
    personnel_certificate_number: str
    time_distribution: list[HourDistribution]
    peak_hours: list[int]
    total_records: int
