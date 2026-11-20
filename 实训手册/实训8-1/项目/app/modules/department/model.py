"""单位表模型：继承 Base，由 create_all 建立 departments 表（教材 6.2）。"""

from sqlalchemy import Column, String

from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"

    dept_code = Column(String(20), primary_key=True)
    full_name = Column(String(100), nullable=False)
    address = Column(String(500))
