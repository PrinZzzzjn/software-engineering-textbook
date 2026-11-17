"""Duty API 入口：创建应用、挂载各模块路由、建表。

第 5 章已有 dept 模块；本章加入 user 模块与数据库，
因此比第 5 章多出：导入 Base/engine、导入用户模型、create_all。
"""

from fastapi import FastAPI

from app.core.database import Base, engine
from app.modules.dept import controller as dept_controller
from app.modules.dept import model as dept_model  # noqa: F401  建表前必须先导入模型
from app.modules.user import controller as user_controller
from app.modules.user import model as user_model  # noqa: F401  建表前必须先导入模型

# 应用对象：所有路由最终都挂在它上面，/docs 页面也由它生成。
app = FastAPI(title="Duty API", version="0.1.0")


# 健康检查：不查数据库、不做业务，只回答“服务是否在运行”。
@app.get("/health")
def health():
    return {"status": "healthy"}


# 每个模块一个 router，前缀统一由这里补 "/api/v1"；模块内只写资源名。
app.include_router(dept_controller.router, prefix="/api/v1")
app.include_router(user_controller.router, prefix="/api/v1")

# 建表：create_all 只识别已导入的模型，上面两行 model 导入不能省。
Base.metadata.create_all(bind=engine)
