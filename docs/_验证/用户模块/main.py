from fastapi import FastAPI

from app.core.database import Base, engine
from app.modules.user import controller as user_controller
from app.modules.user import model  # noqa: F401  建表前必须先导入模型

app = FastAPI(title="Duty API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(user_controller.router, prefix="/api/v1")

Base.metadata.create_all(bind=engine)
