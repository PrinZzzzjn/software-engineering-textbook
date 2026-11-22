from sqlalchemy.orm import Session

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
    total = query.count()
    items = (
        query.order_by(Personnel.certificate_number)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return items, total


def create(db: Session, data):
    personnel = Personnel(**data.model_dump())
    db.add(personnel)
    db.commit()
    db.refresh(personnel)
    return personnel


def update(db: Session, personnel, data: dict):
    for key, value in data.items():
        setattr(personnel, key, value)
    db.commit()
    db.refresh(personnel)
    return personnel


def delete(db: Session, personnel):
    db.delete(personnel)
    db.commit()
