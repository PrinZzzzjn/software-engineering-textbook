# 实训 4-1：接口与设计综合实践

> 对应教材：第 4 章 4.1–4.5 与章末「◆ 综合实训 4-1」
> 学时：4 学时，180 分钟
> 起点：`starter/`（六文件骨架，含 TODO）
> 终点：单位模块六个职责文件 + 五个接口可调用

## 一、任务

本实训以设计为主、代码为辅：

1. 为单位对象写出表结构、接口清单、模块目录三节设计；
2. 用六个文件实现五个接口：列表、详情、新增、修改、删除；
3. 验证 200、201、204、400、404、422；
4. 完成“表字段 ↔ 响应字段”“目录 ↔ 磁盘文件”两组一致性检查。

每一步的语法、代码、命令与检查点见 [分步实现指南.md](分步实现指南.md)。

## 二、完成标准

| 目标 | 验收标志 |
| --- | --- |
| 设计文档 | 表结构、接口清单、模块目录三节齐全；有一条规定性失败 |
| 六文件 | `controller.py`、`service.py`、`crud.py`、`model.py`、`schema.py`、`param.py` 齐全 |
| 五个接口 | `/docs` 中五个单位端点均可执行 |
| 状态码 | 200、201、204、400、404、422 各至少一次真实记录 |
| 列表契约 | 200，返回 `{items, total}`；分页参数真正影响切片 |
| 删除语义 | 204 且响应体为空；重复删除 404 |
| 一致性 | 两组检查逐项通过，有依据 |

## 三、课前准备

- 读过第 3 章 3.3–3.4：五个端点、输入模型、`HTTPException`。
- 读过第 4 章 4.1–4.5：表、模块、接口组、分层、六文件、`Depends`。
- Python 3.10 及以上；`fastapi`、`uvicorn`、`pydantic` 已安装。
- 打开 `starter/`，准备空白设计文档模板与记录表（本目录已提供）。

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
| 0 | 起点与目录结构 | 10 |
| 1 | 设计文档：单位对象 | 25 |
| 2 | `model.py`：dataclass 与内存表 | 20 |
| 3 | `schema.py`：Pydantic 模型 | 20 |
| 4 | `crud.py`：五个存取函数 | 25 |
| 5 | `service.py`：规则与分页 | 30 |
| 6 | `param.py` + `controller.py` + `main.py` | 30 |
| 7 | 状态码验证与两组一致性 | 15 |
| 8 | 提交 | 5 |
| | **合计** | **180** |

## 五、快速开始

在 `starter/` 目录执行：

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

浏览器打开 `http://127.0.0.1:8000/docs`。若空白，打开 `http://127.0.0.1:8000/openapi.json` 或使用教师提供的 `curl` 脚本。

自检包与模型：

```bash
python -c "from app.modules.department import model, schema; print(model.Department.__annotations__); print(schema.DepartmentQueryParams())"
```

预期看到三个字段与 `page=1 page_size=10`。

## 六、排错

| 现象 | 先查什么 | 怎么改 |
| --- | --- | --- |
| `/docs` 打不开 | 是否在 `starter/` 内启动；端口是否被占用 | 用 `python -m uvicorn main:app --port 8000` |
| 业务接口全 404 | `main.py` 是否挂 router；模块前缀 | `include_router(..., prefix="")`；模块 `prefix="/departments"` |
| `ModuleNotFoundError: app` | 当前目录与 `__init__.py` | 回到含 `main.py` 的目录，补齐三个包文件 |
| `NotImplementedError` | 是否还在骨架 | 按阶段补 crud、service、controller |
| 新增仍是 200 | POST 装饰器 | 声明 `status_code=status.HTTP_201_CREATED` |
| 删除是 200 或带正文 | DELETE 装饰器与函数返回 | 声明 204；只调用 service，不返回内容 |
| 重复编码变 422 | 是否把业务重复当字段格式 | service 查重并抛 `HTTPException(400)` |
| 缺字段却进入函数 | 请求体是否仍为 `dict` | 改用 `DepartmentCreate` / `DepartmentUpdate` |
| 分页非法却返回 200 | `DepartmentQueryParams` 与 `Depends()` | 检查 `ge=1`、`le=100` |
| 修改清空了未提交字段 | 是否直接 `model_dump()` | 用 `exclude_unset=True` |
| 输出出现内部字段 | 路由是否缺 `response_model` | 列表 `DepartmentPage`，单条 `DepartmentOut` |
| 重启数据消失 | 是否误以为用了数据库 | 内存版正常；数据库第 6 章引入 |

## 七、提交

1. 设计文档：三节 + 两组一致性检查，不能只抄结论；
2. 六文件代码 + 根 `main.py`；
3. 记录表：200/201/204/400/404/422 各至少一行。

提交前删除 `__pycache__/`、`.pytest_cache/`；不要提交 `venv/`、数据库或 `.env`。

## 八、课后扩展

- 把单位完整改编为自选对象，同步改字段、路径、函数名、设计文档与记录表。
- 增加一个关联对象（如人员所属单位），在“多”的一方加外键。
- 修改一个字段名，记录 model、schema、接口调用方与设计文档的连锁变化。
- 把内存存储改为 JSON 文件，记录只改了哪几个文件。
- 阅读教师测试，理解每个用例在验证什么；不要求课堂默写。
