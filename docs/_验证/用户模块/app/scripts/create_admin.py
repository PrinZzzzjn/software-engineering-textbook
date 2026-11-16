from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.modules.user.model import User


def create_admin(username: str = "admin", password: str = "admin123") -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            db.add(User(
                username=username,
                password_hash=get_password_hash(password),
                role="admin",
            ))
            print(f"已创建管理员：{username}")
        else:
            user.password_hash = get_password_hash(password)
            user.role = "admin"
            print(f"已更新管理员：{username}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
