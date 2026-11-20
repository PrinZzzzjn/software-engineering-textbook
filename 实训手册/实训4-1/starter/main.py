from fastapi import FastAPI

from app.modules.department import controller as department_controller

app = FastAPI(title="Duty API", version="0.1.0")

app.include_router(department_controller.router, prefix="/api/v1")
