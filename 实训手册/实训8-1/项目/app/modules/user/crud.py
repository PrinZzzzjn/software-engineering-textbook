"""用户模块的数据访问：只取用户与写入，不判断规则（教材 8.1）。"""

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
