from sqlalchemy.orm import Session

from app.core.database import commit_or_rollback
from app.core.pagination import paginate
from app.modules.department.model import Department


def get_by_code(db: Session, dept_code: str):
    return db.query(Department).filter(Department.dept_code == dept_code).first()


def list_page(db: Session, offset: int, limit: int, full_name: str | None = None):
    query = db.query(Department)
    if full_name:
        query = query.filter(Department.full_name.contains(full_name))
    query = query.order_by(Department.dept_code)
    return paginate(query, offset, limit)


def create(db: Session, data):
    department = Department(**data.model_dump())
    db.add(department)
    commit_or_rollback(db)
    db.refresh(department)
    return department


def update(db: Session, department, data: dict):
    for key, value in data.items():
        setattr(department, key, value)
    commit_or_rollback(db)
    db.refresh(department)
    return department


def delete(db: Session, department):
    db.delete(department)
    commit_or_rollback(db)
