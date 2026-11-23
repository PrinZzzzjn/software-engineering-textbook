# 实训 3-1：一个资源的四个 HTTP 方法

> 对应教材：第 3 章 3.1–3.4 与章末「◆ 实训 3-1」
> 学时：4 学时，180 分钟
> 起点：`starter/main.py`（空白文件）
> 终点：单文件 FastAPI 服务，五个资源端点可调用

## 一、任务

从一个空文件开始，写出一个可运行的单位接口：

1. 最小应用与 `GET /health`；
2. `GET /departments` 列表，返回 `{items, total}`；
3. `GET /departments/{dept_code}` 详情，不存在返回 404；
4. `POST /departments` 新增，成功 201，缺字段或重复编码 400；
5. `PUT /departments/{dept_code}` 修改，成功 200，不存在 404；
6. `DELETE /departments/{dept_code}` 删除，成功 204 且无正文，重复删除 404。

每一步的语法、代码、命令与检查点见 [分步实现指南.md](分步实现指南.md)。

## 二、完成标准

| 目标 | 验收标志 |
| --- | --- |
| 从空文件启动 | `/docs` 可打开，`/health` 返回 200 与 `{"status": "ok"}` |
| 五个端点可调用 | `/docs` 中五个单位端点均可执行 |
| 状态码齐全 | 200、201、204、400、404 各至少一次真实记录 |
| 删除语义 | 第一次删除 204 且正文为空；第二次 404 |
| 列表契约 | 200，正文同时含 `items` 与 `total` |
| 幂等说明 | 100 字以内，指出 GET、PUT、DELETE 幂等，POST 不幂等，依据是服务器最终状态 |

## 三、课前准备

- 读完教材 3.1–3.4，能区分 HTTP 方法、URL、请求体与状态码。
- Python 3.12 或兼容版本；`fastapi`、`uvicorn` 已安装（教室机通常预装；未装见下方命令）。
- 一个空白 `记录表.md`（本目录已提供）。
- 终端、浏览器；内网环境准备 `/openapi.json` 备用通道。

安装依赖：

```bash
python -m pip install -r requirements.txt
```

内网：

```bash
python -m pip install --no-index --find-links=<wheelhouse 路径> -r requirements.txt
```

## 四、4 学时安排

| 阶段 | 内容 | 分钟 |
| --- | --- | ---: |
| 0 | 环境与操作基础 | 15 |
| 1 | 最小应用与 `/health` | 25 |
| 2 | 字典与列表热身 | 20 |
| 3 | 列表端点 | 20 |
| 4 | 详情端点与 404 | 15 |
| 5 | 新增端点与 201/400 | 25 |
| 6 | 修改端点与 200/404 | 15 |
| 7 | 删除端点与 204/404 | 15 |
| 8 | 验证记录与幂等说明 | 15 |
| 9 | 复核与提交 | 10 |
| | **合计** | **180** |

## 五、快速开始

在 `starter/` 目录执行：

```bash
python -m pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

浏览器打开 `http://127.0.0.1:8000/docs`。若页面空白，打开 `http://127.0.0.1:8000/openapi.json` 或使用教师提供的 `curl` 脚本。

另开终端验证：

```bash
curl -i http://127.0.0.1:8000/health
```

## 六、排错

| 现象 | 先查什么 | 怎么改 |
| --- | --- | --- |
| `ModuleNotFoundError: fastapi` | 依赖是否装在当前 Python | `python -m pip install -r requirements.txt` |
| `Could not import module "main"` | 当前目录有没有 `main.py` | 进入 `starter/`，确认文件名 |
| `/docs` 打不开或空白 | 服务是否启动；内网 CDN | 先看终端是否 `Application startup complete`；空白改用 `/openapi.json` |
| 所有接口 404 | 装饰器路径、HTTP 方法、启动目录 | 对照五个装饰器，统一 `/departments` |
| 新增返回 307 | 集合 URL 末尾斜杠 | 请求和装饰器都写 `/departments` |
| 新增仍返回 200 | 是否声明 `status_code=...201` | 补装饰器参数 |
| 删除返回 200 或带正文 | 是否声明 204；成功路径是否 `return` | 声明 204，删掉 `return` |
| 重复删除仍 200 | 是否先判断存在 | 不存在抛 `HTTPException(404)` |
| 缺字段返回 500 | 是否直接索引 `data["..."]` | 改用 `data.get(...)` 并检查 |
| 修改后字段未变 | 请求体键名与代码读取键名 | 统一 `full_name`、`address` |
| `SyntaxError` | 全角引号、括号、冒号 | 切英文输入法，改成半角 |

## 七、提交

1. 可独立启动的 `main.py`；
2. 填好的 `记录表.md`（200/201/204/400/404 各至少一行，实际值真实）；
3. 100 字以内幂等说明。

不要提交 `venv/`、`__pycache__/`、教师答案或自动测试。

## 八、课后扩展

- 给列表加 `page`、`page_size` 查询参数，观察非法值。
- 把 `data: dict` 改成 Pydantic 模型，对比 400 与 422。
- 解释为什么“编码重复”由函数内判断返回 400，而不是框架校验。
- 回看教材 3.3.4，指出每个成功或失败响应由装饰器、函数还是框架产生。
