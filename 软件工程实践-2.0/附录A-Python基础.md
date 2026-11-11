# 附录 A Python 基础（最小可用集）

本附录只补本书会用到的语法。看懂它就能跟上第 5 章及之后的全部代码；更完整的语法请查 Python 官方教程。

## A.1 变量与常用类型

```python
name = "值班系统"      # str 字符串
count = 12            # int 整数
ratio = 0.85          # float 浮点数
enabled = True        # bool 布尔值，只有 True / False
items = ["甲", "乙"]   # list 列表，可增删
config = {"port": 8000}  # dict 字典，键 → 值
nothing = None        # 空值，常用于「还没有填」
```

`list` 用 `items.append("丙")` 追加、`items[0]` 取第一个；`dict` 用 `config["port"]` 取值、`config.get("port", 8000)` 在键不存在时给默认值。

## A.2 函数与参数

```python
def greet(name: str, times: int = 1) -> str:
    return ("你好，" + name + "\n") * times
```

- `name: str` 是**类型注解**：说明期望传入字符串，不是强制检查；`-> str` 说明返回值类型。
- `times: int = 1` 是**默认参数**，不传就用 1。
- 调用：`greet("张三")`、`greet("张三", times=2)`。

## A.3 类与对象

```python
class Department:
    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name

    def label(self) -> str:
        return f"{self.code} {self.name}"

dept = Department("D01", "一中队")
print(dept.label())
```

`class` 定义一类数据的「字段 + 行为」；`__init__` 在创建对象时执行；`self` 指当前对象。本书第 5 章的 Pydantic `BaseModel`、第 10 章的 ORM 模型都是这个思路的延伸：先声明「数据长什么样」，再创建对象。

## A.4 装饰器

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

`@app.get(...)` 写在函数上方，意思是「把下面这个函数登记到这条路径上」。装饰器本质是「接收函数、加工后再返回」的函数；本书只要知道它起登记作用即可，不必自己写装饰器。第 5 章 5.1.1 会再讲一次。

## A.5 导入、模块与包

```python
from fastapi import FastAPI, APIRouter
from app.core.database import get_db
```

`from X import Y` 表示从模块 X 里拿 Y 来用。带点号的路径（`app.core.database`）对应目录 `app/core/database.py`；一个目录里有 `__init__.py` 就成为一个包。导入失败时先检查：文件名是否拼对、当前目录是否是项目根目录、虚拟环境是否已激活。

## A.6 虚拟环境（每次开工第一步）

```bash
$ python -m venv .venv
$ .venv\Scripts\activate        # Windows
$ source .venv/bin/activate     # Linux / macOS
$ pip install -r requirements.txt
```

激活后命令行前缀会出现 `(.venv)`。换机器、换终端都要重新激活；把依赖写进 `requirements.txt`，别靠记忆装包。

## A.7 三个最常见的报错

| 看到什么 | 通常原因 | 先查哪里 |
| --- | --- | --- |
| `ModuleNotFoundError` | 包没装，或虚拟环境没激活 | `pip list`、命令行前缀 |
| `IndentationError` | 缩进混用了空格与 Tab | 报错行的前一行 |
| `KeyError` / `TypeError: ... NoneType` | 字典键不存在，或函数返回了 `None` | 取值前用 `.get()`、检查返回路径 |

> 看报错先读最后一行：异常类型 + 消息；再往上找自己写的第一个文件名与行号。
