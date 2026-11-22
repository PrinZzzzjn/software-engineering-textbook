from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.duty_record import crud
from app.modules.personnel.crud import (
    get_by_certificate_number as get_personnel_by_certificate_number,
)
from app.modules.workstation.crud import get_by_id as get_workstation_by_id


def _validate_duty_record(db: Session, data):
    """按规则清单的顺序校验；全部通过后才允许写入。

    顺序：时间顺序（不查库）→ 人员（一次查询）→ 哨位（一次查询）→ 重叠（范围查询）。
    任何一条失败都抛 400，控制器与 crud 不会执行到 commit。
    """
    # 规则一：开始时间必须早于结束时间（跨字段）
    if data.start_time >= data.end_time:
        raise HTTPException(status_code=400, detail="开始时间必须早于结束时间")

    # 规则二：人员和哨位必须存在（跨表）
    if not get_personnel_by_certificate_number(
        db, data.personnel_certificate_number
    ):
        raise HTTPException(status_code=400, detail="人员不存在")
    if not get_workstation_by_id(db, data.workstation_id):
        raise HTTPException(status_code=400, detail="哨位不存在")

    # 规则三：同一哨位的时间不能重叠（跨记录）
    conflicts = crud.find_overlap(
        db, data.workstation_id, data.start_time, data.end_time
    )
    if conflicts:
        raise HTTPException(status_code=400, detail="该哨位在该时段已有执勤安排")


def list_duty_records(db, params):
    offset = (params.page - 1) * params.page_size
    items, total = crud.list_page(
        db,
        offset,
        params.page_size,
        params.personnel_certificate_number,
        params.workstation_id,
    )
    return {"items": items, "total": total}


def create_duty_record(db, data):
    """先完成全部校验，再写入；校验过程中不 commit。"""
    _validate_duty_record(db, data)
    return crud.create(db, data)


def get_duty_record(db, record_id: int):
    record = crud.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="执勤记录不存在")
    return record


def delete_duty_record(db, record_id: int) -> None:
    record = crud.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="执勤记录不存在")
    crud.delete(db, record)
