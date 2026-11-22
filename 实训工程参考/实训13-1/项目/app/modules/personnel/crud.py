from sqlalchemy.orm import Session

from app.core.database import commit_or_rollback
from app.core.pagination import paginate
from app.modules.personnel.model import Personnel


def get_by_certificate_number(db: Session, certificate_number: str):
    return (
        db.query(Personnel)
        .filter(Personnel.certificate_number == certificate_number)
        .first()
    )


def list_page(
    db: Session,
    offset: int,
    limit: int,
    name: str | None = None,
    dept_code: str | None = None,
):
    query = db.query(Personnel)
    if name:
        query = query.filter(Personnel.name.contains(name))
    if dept_code:
        query = query.filter(Personnel.dept_code == dept_code)
    query = query.order_by(Personnel.certificate_number)
    return paginate(query, offset, limit)


def create(db: Session, data):
    personnel = Personnel(**data.model_dump())
    db.add(personnel)
    commit_or_rollback(db)
    db.refresh(personnel)
    return personnel


def update(db: Session, personnel, data: dict):
    for key, value in data.items():
        setattr(personnel, key, value)
    commit_or_rollback(db)
    db.refresh(personnel)
    return personnel


def delete(db: Session, personnel):
    db.delete(personnel)
    commit_or_rollback(db)
