from sqlalchemy.orm import Session

from app.modules.department.model import Department


def get_by_code(db: Session, dept_code: str):
    return db.query(Department).filter(Department.dept_code == dept_code).first()


def list_page(db: Session, offset: int, limit: int):
    items = (
        db.query(Department)
        .offset(offset)
        .limit(limit)
        .all()
    )
    total = db.query(Department).count()
    return items, total


def create(db: Session, data):
    department = Department(**data.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


def update(db: Session, department, data: dict):
    for key, value in data.items():
        setattr(department, key, value)
    db.commit()
    db.refresh(department)
    return department


def delete(db: Session, department):
    db.delete(department)
    db.commit()
