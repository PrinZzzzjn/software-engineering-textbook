"""数据库基础设施：引擎、会话工厂、Base 与请求级会话依赖。

对应教材 6.1。第 5 章的数据放在内存列表里，服务一停就丢；
本章把用户写到项目根目录的 duty.db。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 数据库文件的位置：项目根目录下的 duty.db，由 main.py 启动时建表。
DATABASE_URL = "sqlite:///./duty.db"

# engine 管“怎么连”；check_same_thread=False 是 SQLite 在多请求下的要求。
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal 不是会话本身，而是“会话工厂”：调用一次得到一个新的 session。
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 表模型的父类：User 继承它，SQLAlchemy 才知道该类对应一张表。
Base = declarative_base()


def get_db():
    """每个请求开一个 session，交给接口，请求结束后关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
