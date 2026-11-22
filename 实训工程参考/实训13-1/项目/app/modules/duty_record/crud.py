from sqlalchemy.orm import Session

from app.core.database import commit_or_rollback
from app.core.pagination import paginate
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
    query = query.order_by(DutyRecord.id)
    return paginate(query, offset, limit)


def find_overlap(db: Session, workstation_id: str, start_time, end_time):
    """查同一哨位上、与给定时间段重叠的第一条执勤记录。

    重叠条件：已有开始 < 新结束 且 已有结束 > 新开始。
    首尾相接（已有结束 == 新开始）不满足第二个条件，不算冲突。
    只需要判断“是否存在”，取 first 而不是 all，避免把整段冲突记录搬到内存。
    """
    return (
        db.query(DutyRecord)
        .filter(
            DutyRecord.workstation_id == workstation_id,
            DutyRecord.start_time < end_time,
            DutyRecord.end_time > start_time,
        )
        .first()
    )


def create_many(db: Session, rows):
    """一个批次一个事务：全部 add 后只提交一次；失败回滚并继续抛出。"""
    records = [DutyRecord(**row.model_dump()) for row in rows]
    db.add_all(records)
    commit_or_rollback(db)
    for record in records:
        db.refresh(record)
    return records


def delete(db: Session, record):
    db.delete(record)
    commit_or_rollback(db)
