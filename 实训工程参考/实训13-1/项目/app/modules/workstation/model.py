from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Workstation(Base):
    __tablename__ = "workstations"

    workstation_id = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    dept_code = Column(String(20), nullable=False)
    is_active = Column(Integer, default=1)
