# 综合实训 4-1 完成态项目

这是教材 4.5 的六文件内存版单位模块。数据只保存在当前进程，重启后清空；无数据库、认证和接口版本前缀。

## 启动

要求 Python 3.10 及以上。在本目录执行：

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

浏览器打开 <http://127.0.0.1:8000/docs>，可调用 `/departments` 的五个接口；`GET /health` 返回服务状态。停止服务按 `Ctrl+C`。

## 自动测试

测试依赖不属于运行依赖，教师验证时另装：

```powershell
python -m pip install httpx pytest
python -m pytest tests/test_api.py
```

测试覆盖 200、201、204、400、404、422，以及默认分页、指定页、空页和非法分页参数。
