from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.analytics import service
from app.modules.analytics.schema import DutyTimeDistribution, StaffDutyYearly

router = APIRouter(prefix="/analytics", tags=["统计分析"])


@router.get("/staff-duty-yearly", response_model=StaffDutyYearly)
def staff_duty_yearly(
    personnel_certificate_number: str = Query(...),
    year: str = Query(...),
    db: Session = Depends(get_db),
):
    return service.get_staff_duty_yearly(db, personnel_certificate_number, year)


@router.get("/duty-time-distribution", response_model=DutyTimeDistribution)
def duty_time_distribution(
    personnel_certificate_number: str = Query(...),
    year: str = Query(...),
    db: Session = Depends(get_db),
):
    return service.get_duty_time_distribution(db, personnel_certificate_number, year)
