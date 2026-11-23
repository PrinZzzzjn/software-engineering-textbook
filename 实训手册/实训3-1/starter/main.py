# 实训 3-1 起点：从空文件写出最小应用与五个端点。
#
# 第 1 步目标：
# 1. 导入 FastAPI
# 2. 创建 app = FastAPI()
# 3. 加一个 GET /health 端点，返回 {"status": "ok"}
#
# 写完启动：
# uvicorn main:app --reload --port 8000
#
# 打开 http://127.0.0.1:8000/docs 应能看到 /health。
# 如果 /docs 空白，改用 http://127.0.0.1:8000/openapi.json 查看接口清单。
