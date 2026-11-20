from fastapi import FastAPI

from app.core.database import Base, engine
from app.modules.department import controller as department_controller
from app.modules.department import model  # noqa: F401  create_all 需要先导入模型

app = FastAPI(title="Duty API", version="0.1.0")

Base.metadata.create_all(bind=engine)
app.include_router(department_controller.router, prefix="/api/v1")
