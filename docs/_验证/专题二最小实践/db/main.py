from fastapi import FastAPI

from app.core.database import Base, engine
from app.modules.dept import controller as dept_controller
from app.modules.dept import model  # noqa: F401  create_all 需要先导入模型

app = FastAPI(title="Duty API", version="0.1.0")

Base.metadata.create_all(bind=engine)
app.include_router(dept_controller.router, prefix="/api/v1")
