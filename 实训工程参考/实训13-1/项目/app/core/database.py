import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./duty.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """请求级会话：正常结束由各写操作自行提交；出现异常先回滚再向上抛。"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def commit_or_rollback(db: Session) -> None:
    """一个业务动作一次提交；失败回滚并继续抛出，避免半批数据与脏会话。

    对应教材 13.2 的三条纪律：commit 放在业务动作最后、异常要 rollback、
    只读接口不调用本函数。
    """
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
