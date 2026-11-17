from fastapi import FastAPI

from app.modules.dept import controller as dept_controller

app = FastAPI(title="Duty API", version="0.1.0")

app.include_router(dept_controller.router, prefix="/api/v1")
