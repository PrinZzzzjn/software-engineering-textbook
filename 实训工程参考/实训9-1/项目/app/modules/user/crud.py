from sqlalchemy.orm import Session

from app.modules.user.model import User


def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def list_all(db: Session) -> list[User]:
    return db.query(User).order_by(User.id).all()


def create(db: Session, username: str, password_hash: str) -> User:
    user = User(username=username, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, user: User, changes: dict) -> User:
    for field, value in changes.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def list_page(db: Session, offset: int, limit: int):
    """复用第 7 章的分页骨架：同一个 query 计数与取页，固定按 id 升序。"""
    query = db.query(User)
    total = query.count()
    items = query.order_by(User.id).offset(offset).limit(limit).all()
    return items, total
