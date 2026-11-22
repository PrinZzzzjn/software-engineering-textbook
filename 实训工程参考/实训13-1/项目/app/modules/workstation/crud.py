from sqlalchemy.orm import Session

from app.core.database import commit_or_rollback
from app.core.pagination import paginate
from app.modules.workstation.model import Workstation


def get_by_id(db: Session, workstation_id: str):
    return (
        db.query(Workstation)
        .filter(Workstation.workstation_id == workstation_id)
        .first()
    )


def list_page(db: Session, offset: int, limit: int, dept_code: str | None = None):
    query = db.query(Workstation)
    if dept_code:
        query = query.filter(Workstation.dept_code == dept_code)
    query = query.order_by(Workstation.workstation_id)
    return paginate(query, offset, limit)


def create(db: Session, data):
    workstation = Workstation(**data.model_dump())
    db.add(workstation)
    commit_or_rollback(db)
    db.refresh(workstation)
    return workstation


def update(db: Session, workstation, data: dict):
    for key, value in data.items():
        setattr(workstation, key, value)
    commit_or_rollback(db)
    db.refresh(workstation)
    return workstation


def delete(db: Session, workstation):
    db.delete(workstation)
    commit_or_rollback(db)
