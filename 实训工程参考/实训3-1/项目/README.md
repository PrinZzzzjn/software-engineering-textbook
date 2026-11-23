# 实训 3-1 完成态项目

这是教材 3.3.4 代码 3-3-5、3-3-6 的可运行版本：一个 `main.py`、一个内存字典、五个 `/departments` 端点，另含最小应用一步练习用的 `/health`。进程重启后，数据恢复为 D01 一条记录。

## 启动

在本目录执行：

```powershell
python -m pip install -r requirements.txt
uvicorn main:app --port 8000
```

打开 `http://127.0.0.1:8000/docs`，可依次调用 `/health` 与列表、详情、新增、修改、删除接口。服务地址为 `http://127.0.0.1:8000`。

## 接口契约

| 方法与路径 | 成功响应 | 失败响应 |
| --- | --- | --- |
| `GET /health` | 200，`{"status": "ok"}` | — |
| `GET /departments` | 200，`{items, total}` | — |
| `GET /departments/{dept_code}` | 200，单条记录 | 404 |
| `POST /departments` | 201，新建记录 | 缺字段或编码重复为 400 |
| `PUT /departments/{dept_code}` | 200，修改后的记录 | 404 |
| `DELETE /departments/{dept_code}` | 204，无响应体 | 404 |

## 自动验证

测试工具不计入运行依赖，需另行安装：

```powershell
python -m pip install httpx pytest
python -m pytest tests/test_api.py
```

十一项测试覆盖 `/health`、列表与详情成功、详情不存在、新增、重复编码、缺字段、修改、修改不存在、删除无正文及重复删除。每个测试开始前都会重置内存数据，因此可独立、重复执行。
