"""单位模块的数据访问：只取数与写入，不判断规则（教材 6.2）。"""

from sqlalchemy.orm import Session

from app.core.pagination import paginate

from . import model


def list_page(db: Session, offset: int, limit: int) -> tuple[list[model.Department], int]:
    query = db.query(model.Department).order_by(model.Department.dept_code)
    return paginate(query, offset, limit)


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
