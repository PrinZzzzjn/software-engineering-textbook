# 实训 3-1 起点

本目录只提供依赖声明和一张空白起点，不提供可运行应用。学生从 `main.py` 开始，按教材「◆ 实训 3-1」的步骤自己写出五个端点。

## 安装依赖

```powershell
python -m pip install -r requirements.txt
```

## 任务顺序

1. 最小应用：`app = FastAPI()` 与 `GET /health`
2. 列表端点：先返回一条写死记录，再改为 `DEPARTMENTS` 字典
3. 详情端点：`GET /departments/{dept_code}`，不存在返回 404
4. 新增端点：`POST /departments`，成功 201，缺字段或编码重复 400
5. 修改端点：`PUT /departments/{dept_code}`，成功 200，不存在 404
6. 删除端点：`DELETE /departments/{dept_code}`，成功 204，不存在 404
7. 验证并填写状态码记录表，写 100 字以内幂等性说明
8. 重启复核并提交

## 启动与验证

在 `main.py` 所在目录执行：

```powershell
uvicorn main:app --reload --port 8000
```

浏览器打开 `http://127.0.0.1:8000/docs`，每完成一步就刷新一次，确认新端点出现并能调用。
