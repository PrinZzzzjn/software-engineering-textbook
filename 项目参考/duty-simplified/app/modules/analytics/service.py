from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import extract
from sqlalchemy.orm import Session

from app.modules.duty_record.model import DutyRecord
from app.modules.personnel.model import Personnel


def _load_records(db: Session, cert: str, year: str) -> list[DutyRecord]:
    """校验输入并按人员与年份取记录；输入不合法时抛 400。"""
    if len(year) != 4 or not year.isdigit():
        raise HTTPException(status_code=400, detail="年份格式错误")

    person = db.query(Personnel).filter(
        Personnel.certificate_number == cert
    ).first()
    if person is None:
        raise HTTPException(status_code=400, detail="人员不存在")

    return db.query(DutyRecord).filter(
        DutyRecord.personnel_certificate_number == cert,
        extract("year", DutyRecord.start_time) == int(year),
    ).all()


def get_staff_duty_yearly(db: Session, cert: str, year: str) -> dict:
    """年度统计：天数去重、时长累加、月份补齐 12 项。"""
    records = _load_records(db, cert, year)

    total_hours = 0.0
    days = set()
    monthly_days = {m: set() for m in range(1, 13)}
    monthly_hours = {m: 0.0 for m in range(1, 13)}

    for r in records:
        hours = (r.end_time - r.start_time).total_seconds() / 3600
        total_hours += hours
        current = r.start_time.date()
        end_date = r.end_time.date()
        while current <= end_date:
            days.add(current)
            monthly_days[r.start_time.month].add(current)
            current += timedelta(days=1)
        monthly_hours[r.start_time.month] += hours

    return {
        "personnel_certificate_number": cert,
        "year": year,
        "total_duty_days": len(days),
        "total_duty_hours": round(total_hours, 2),
        "duty_by_month": [
            {
                "month": m,
                "days": len(monthly_days[m]),
                "hours": round(monthly_hours[m], 2),
            }
            for m in range(1, 13)
        ],
    }


def get_duty_time_distribution(db: Session, cert: str, year: str) -> dict:
    """时段分布：按开始小时计数，补齐 24 项，高峰可并列。"""
    records = _load_records(db, cert, year)

    hour_counts = {h: 0 for h in range(24)}
    for r in records:
        hour_counts[r.start_time.hour] += 1

    max_count = max(hour_counts.values()) if records else 0
    peak_hours = [h for h, c in hour_counts.items() if c == max_count] if max_count else []

    return {
        "year": year,
        "personnel_certificate_number": cert,
        "time_distribution": [{"hour": h, "count": c} for h, c in hour_counts.items()],
        "peak_hours": peak_hours,
        "total_records": len(records),
    }
