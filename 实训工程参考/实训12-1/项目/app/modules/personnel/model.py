from sqlalchemy import Column, String

from app.core.database import Base


class Personnel(Base):
    __tablename__ = "personnel"

    certificate_number = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    dept_code = Column(String(20), nullable=False)
    rank = Column(String(50), nullable=True)
