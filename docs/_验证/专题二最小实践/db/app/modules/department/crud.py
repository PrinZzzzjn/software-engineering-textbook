from sqlalchemy.orm import Session

from . import model


def list_all(db: Session) -> list[model.Department]:
    return db.query(model.Department).all()


def get(db: Session, dept_code: str) -> model.Department | None:
    return (
        db.query(model.Department)
        .filter(model.Department.dept_code == dept_code)
        .first()
    )


def create(db: Session, item: model.Department) -> model.Department:
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update(db: Session, item: model.Department, data: dict) -> model.Department:
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, item: model.Department) -> None:
    db.delete(item)
    db.commit()
