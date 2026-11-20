from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.duty_record import service
from app.modules.duty_record.param import DutyRecordQueryParams
from app.modules.duty_record.schema import DutyRecordCreate, DutyRecordOut

router = APIRouter(prefix="/duty-records", tags=["执勤记录"])


@router.get("")
def list_duty_records(
    params: DutyRecordQueryParams = Depends(),
    db: Session = Depends(get_db),
):
    return service.list_duty_records(db, params)


@router.post("", response_model=DutyRecordOut, status_code=status.HTTP_201_CREATED)
def create_duty_record(data: DutyRecordCreate, db: Session = Depends(get_db)):
    return service.create_duty_record(db, data)


@router.get("/{record_id}", response_model=DutyRecordOut)
def read_duty_record(record_id: int, db: Session = Depends(get_db)):
    return service.get_duty_record(db, record_id)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_duty_record(record_id: int, db: Session = Depends(get_db)):
    service.delete_duty_record(db, record_id)
