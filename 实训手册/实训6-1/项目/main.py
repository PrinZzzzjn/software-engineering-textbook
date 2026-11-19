"""Duty API 入口：创建应用、挂载各模块路由。

第 5 章只有 dept 一个模块；本章加入内存版 user 模块，
因此比第 5 章多出一行 user 路由挂载。用户数据在内存里，不需要建表；
第 8 章引入数据库时才会在这里加 database.py 与 create_all。
"""

from fastapi import FastAPI

from app.modules.dept import controller as dept_controller
from app.modules.user import controller as user_controller

# 应用对象：所有路由最终都挂在它上面，/docs 页面也由它生成。
app = FastAPI(title="Duty API", version="0.1.0")


# 健康检查：不查数据库、不做业务，只回答“服务是否在运行”。
@app.get("/health")
def health():
    return {"status": "healthy"}


# 每个模块一个 router，前缀统一由这里补 "/api/v1"；模块内只写资源名。
app.include_router(dept_controller.router, prefix="/api/v1")
app.include_router(user_controller.router, prefix="/api/v1")
