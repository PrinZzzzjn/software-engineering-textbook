"""Duty API 入口：只负责创建应用与挂载路由。

对应教材第 5 章 5.1：入口不写业务代码。
第 6 章会在这里补建表三行：导入 Base 与 engine、导入模型、调用 create_all。
"""

from fastapi import FastAPI

from app.modules.workstation import controller as workstation_controller

# 应用对象：所有路由最终都挂在它上面，/docs 页面也由它生成。
app = FastAPI(title="Duty API", version="0.1.0")


# 健康检查：不查数据库、不做业务，只回答“服务是否在运行”。部署后也是第一项可用性证据。
@app.get("/health")
def health():
    return {"status": "healthy"}


# 把模块路由挂到应用。模块 router 的前缀是 "/workstations"，这里再加 "/api/v1"，
# 两段相加才是完整路径 /api/v1/workstations/；缺一段就会出现 404。
app.include_router(workstation_controller.router, prefix="/api/v1")
