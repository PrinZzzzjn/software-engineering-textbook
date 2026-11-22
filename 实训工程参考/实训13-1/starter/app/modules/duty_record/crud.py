from sqlalchemy.orm import Session

from app.modules.duty_record.model import DutyRecord


def get_by_id(db: Session, record_id: int):
    return db.query(DutyRecord).filter(DutyRecord.id == record_id).first()


def list_page(
    db: Session,
    offset: int,
    limit: int,
    personnel_certificate_number: str | None = None,
    workstation_id: str | None = None,
):
    query = db.query(DutyRecord)
    if personnel_certificate_number:
        query = query.filter(
            DutyRecord.personnel_certificate_number == personnel_certificate_number
        )
    if workstation_id:
        query = query.filter(DutyRecord.workstation_id == workstation_id)
    total = query.count()
    items = query.order_by(DutyRecord.id).offset(offset).limit(limit).all()
    return items, total


def find_overlap(db: Session, workstation_id: str, start_time, end_time):
    """查同一哨位上、与给定时间段重叠的执勤记录。

    重叠条件：已有开始 < 新结束 且 已有结束 > 新开始。
    首尾相接（已有结束 == 新开始）不满足第二个条件，不算冲突。
    """
    return (
        db.query(DutyRecord)
        .filter(
            DutyRecord.workstation_id == workstation_id,
            DutyRecord.start_time < end_time,
            DutyRecord.end_time > start_time,
        )
        .all()
    )


def create(db: Session, data):
    record = DutyRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def delete(db: Session, record):
    db.delete(record)
    db.commit()
