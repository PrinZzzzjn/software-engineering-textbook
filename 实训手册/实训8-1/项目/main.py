"""Duty API 入口：创建应用、挂载各模块路由、建表。

第 6 章建立 app/core/database.py 与 departments 表；本章加入 users 表。
create_all 只识别已导入的模型，因此两个模型都要先导入。
"""

from fastapi import FastAPI

from app.core.database import Base, engine
from app.modules.department import controller as department_controller
from app.modules.department import model as department_model  # noqa: F401  建表前先导入模型
from app.modules.user import controller as user_controller
from app.modules.user import model as user_model  # noqa: F401  建表前先导入模型

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Duty API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "healthy"}


# 每个模块一个 router，前缀统一由这里补 "/api/v1"；模块内只写资源名。
app.include_router(department_controller.router, prefix="/api/v1")
app.include_router(user_controller.router, prefix="/api/v1")
