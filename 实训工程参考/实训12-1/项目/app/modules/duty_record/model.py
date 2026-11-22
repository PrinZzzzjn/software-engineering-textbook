from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base


class DutyRecord(Base):
    __tablename__ = "duty_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    personnel_certificate_number = Column(String(20), nullable=False)
    workstation_id = Column(String(20), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="normal")
