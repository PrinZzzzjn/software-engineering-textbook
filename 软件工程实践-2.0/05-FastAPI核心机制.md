# 第 5 章 FastAPI 核心机制

> **节首信息条**｜对应课次 4 · 后端开发框架基础（与第 4 章合占 2 学时 · 理论讲授，只计一次）｜**本单元第 2/2 章**｜前置：第 4 章《HTTP 与接口设计》；Python 语法不熟不要慌，本章的补课卡会补｜**本节活动**：◇ 课堂活动块（听讲要点 / 讨论·演示 / 课后自测 / 回链）

第 4 章末尾用 `@app.get` 写了两个最小接口。但从第 7 章的项目初始化开始，实战代码会连续出现一批新面孔：`APIRouter`、`BaseModel`、`Field`、`Depends`、`HTTPException`、`get_db`……如果这些符号第一次见面就出现在整屏代码里，你只能“照着敲”，不知道每一行为什么存在。

本章把这些机制集中讲一遍：每节只讲一件事，配一张 150–200 字的补课卡。读到看不懂的 Python 语法（装饰器、类型注解、`Optional`），直接跳到该节末尾的补课卡，看完再回来——卡片就是为“绕路”设计的。5.1.9 的完整最小工程建议在自己电脑上敲一遍：只敲三个文件，就能把 5.1.2–5.1.6 的机制全部摸一遍。读完本章，第 7–15 章的后端代码你都能“读得懂、改得动”。

## 本章学习目标

读完第 5 章，你应该能：

1. 用一句话说明 FastAPI 是什么、本书为什么选它而不是 Flask 或 Django。
2. 解释 `@app.get("...")` 装饰器把“URL + 方法”与函数绑定的过程，并读懂带类型注解的函数签名。
3. 说出 `APIRouter` 与 `include_router` 各自解决的问题，指出 `router` 对象从哪里来。
4. 用 `BaseModel` 与 `Field` 定义一个带约束的输入模型，并解释 422 错误产生在哪一层。
5. 说明 `Depends` “把公共逻辑抽成参数”的含义，能看懂 `get_db` 一类的依赖写法。
6. 对照 5.1.8 节的回链表，说出 JWT、ORM 等概念分别会在哪一章完整展开。

## 前置知识卡

开始本章前，请确认你已经具备：

| # | 你需要会 | 不会就回看 |
| --- | --- | --- |
| 1 | HTTP 方法、状态码与接口四要素 | 第 4 章 4.1.2–4.1.7 |
| 2 | Python 函数、字典与 f 字符串 | 附录 A《Python 基础》 |
| 3 | 在终端进入目录、执行命令 | 附录 A《Python 基础》 |
| 4 | 装饰器与类型注解（只要求看懂） | 本章 5.1.2、补课卡 K-01、K-02 |

本章不预设你会高级 Python 语法——缺什么补什么，各节末尾的补课卡就是为此准备的。8 张补课卡与所在节的对照如下：

| 卡号 | 主题 | 所在节 |
| --- | --- | --- |
| K-01 | 装饰器 | 5.1.2 |
| K-02 | Python 类与类型注解 | 5.1.2 |
| K-03 | APIRouter | 5.1.3 |
| K-04 | Pydantic | 5.1.4 |
| K-05 | HTTPException | 5.1.5 |
| K-06 | Depends 与依赖注入 | 5.1.6 |
| K-07 | ORM 与 SQLAlchemy | 5.1.7 |
| K-08 | Optional 与 Literal | 5.1.7 |

## 5.1 概念讲解

### 5.1.1 FastAPI 是什么，为什么选它

FastAPI 是一个用 Python 写 Web 接口的框架：你定义函数，它负责把 HTTP 请求接进来、把返回值变成 JSON。与另外两个常见框架的一句话对比：

| 框架 | 一句话定位 |
| --- | --- |
| Django | “全家桶”：自带后台、表单、用户系统，适合大而全的网站 |
| Flask | “积木盒”：核心极简，其余自己搭，灵活但要自己选型 |
| FastAPI | “接口优先”：类型注解驱动的校验与自动文档，天生适合写 API |

本书选 FastAPI 的理由就两条：参数校验写在函数签名里，不用手写一堆 `if`；接口文档自动生成，联调时前后端有共同参照。什么时候不用它？如果产品是“以页面为主、接口很少”的传统网站，Django 那套全家桶反而省事。

### 5.1.2 app 实例与装饰器路由

第 4 章已经见过这两段代码，这里把机制说透。

**代码 5-1-1** · `main.py`（最小应用，Python）

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"你好，{name}"}
```

`app = FastAPI()` 造出一个应用对象，它是所有路由的挂载点。`@app.get("/hello/{name}")` 是一个装饰器：它把下面的函数登记到 `app` 上，规则是“有人用 GET 访问 `/hello/xxx` 时，调用这个函数，并把 `xxx` 传给 `name`”。函数返回字典，框架负责转成 JSON。

注意 `name: str` 这个写法：冒号后面是类型注解。FastAPI 会读它，先做转换与校验，再进入函数体——这就是第 4 章 `/square/abc` 返回 422 的原因。装饰器与类型注解的 Python 语法背景，见下面两张卡。

> **补课卡 K-01 · 装饰器（decorator）**
> **是什么**：装饰器是“接收一个函数、返回一个新函数”的语法糖，写成 `@名字` 放在函数上方。
> **为什么需要**：把“登记路由”这类重复的登记动作从函数体里拿出来，交给框架统一处理。
> **最小例子**：`@app.get("/x")` 之下的函数，会被登记为“GET /x”的处理函数。
> **什么时候用**：本书里你不需要自己写装饰器，只需要看懂 `@xxx` 意味着“这个函数被登记或包装了”。

> **补课卡 K-02 · Python 类与类型注解**
> **是什么**：`class` 把数据与操作打包成一种新类型；`name: str`、`-> int` 这类写法是类型注解，标明变量或返回值的预期类型。
> **为什么需要**：注解本身不改变运行结果，但 FastAPI 会读取它做校验，编辑器也靠它给出提示。
> **最小例子**：`def add(a: int, b: int) -> int: return a + b`。
> **什么时候用**：写 FastAPI 接口时几乎每个函数签名都要用；暂时不会写复杂的类，不影响学本书。

### 5.1.3 APIRouter：把路由拆到各模块

项目变大后，几十个接口都挂在 `app` 上，`main.py` 会乱成一团长文件。`APIRouter` 是“小一号的挂载点”：各业务模块各自建一个 `router`，写好自己的接口；主文件再用 `include_router` 把它们组装回 `app`。这里的“模块”指按业务对象划分的一组接口与代码，例如部门模块、人员模块；第 6 章 6.1.3 会正式讲模块划分，本章只需知道一个模块通常对应一个 router 文件。

**代码 5-1-2** · `app/routers/departments.py`（路由模块，Python）

```python
from fastapi import APIRouter

router = APIRouter(prefix="/departments", tags=["部门"])

@router.get("")
def list_departments():
    return {"items": [], "total": 0}
```

**代码 5-1-3** · `main.py`（组装，Python）

```python
from fastapi import FastAPI

from app.routers import departments

app = FastAPI()

app.include_router(departments.router, prefix="/api/v1")
```

所以后面章节看到 `@router.get(...)` 时，`router` 不是凭空出现的——它由本模块顶部的 `APIRouter(...)` 创建，最终被 `main.py` 的 `include_router` 挂进应用。这条“创建—挂载”链路，是第 7 章项目初始化的核心动作。

> **补课卡 K-03 · APIRouter**
> **是什么**：FastAPI 提供的“子挂载点”，用法和 `app` 一样，可以注册路由，还能统一加上前缀和标签。
> **为什么需要**：接口多了以后全写在一个文件里没法维护；按业务拆成模块，各管各的路由。
> **最小例子**：`router = APIRouter(prefix="/departments")`，然后 `@router.get("")`。
> **什么时候用**：从第 7 章起，本书每个业务模块一个 router 文件，`main.py` 只负责组装。

### 5.1.4 三类参数与 Pydantic 模型

接口的参数只有三个位置：路径、查询串、请求体。

**代码 5-1-4** · `app/routers/departments.py`（三类参数，Python）

```python
@router.get("/{dept_id}")                     # ① 路径参数：定位“某一个”
def read_department(dept_id: int):
    return {"id": dept_id}

@router.get("")                               # ② 查询参数：筛选、分页，不填有默认值
def list_departments(page: int = 1, page_size: int = 10):
    return {"page": page, "page_size": page_size}

@router.post("")                              # ③ 请求体：提交一份数据
def create_department(data: DepartmentCreate):
    return data
```

③ 的 `DepartmentCreate` 是一个 Pydantic 模型——请求体不再是零散参数，而是一个有名字、有约束的结构：

**代码 5-1-5** · `schemas.py`（输入模型，Python）

```python
from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    dept_code: str = Field(..., min_length=2, max_length=10)
    dept_name: str = Field(..., min_length=2, max_length=50)
```

`...` 表示必填；`min_length`、`max_length` 是约束。提交 `{"dept_code": "D"}` 会在进入函数前得到 422，响应 `detail` 里指明是哪个字段、违反了什么。

输入与输出分开定义是铁律。第 8 章的用户表里有 `password_hash`，但它绝不能出现在返回里——输出要另建一个只含公开字段的模型。两个模型长什么样、怎么配合，见第 8 章 8.1.4。

> **补课卡 K-04 · Pydantic**
> **是什么**：用 Python 类定义数据结构并自动校验的库；`BaseModel` 是基类，`Field` 用来加约束。
> **为什么需要**：把“字段名、类型、长度限制”写在一处，请求进来先校验，不合格直接 422，函数体里不用再写 `if`。
> **最小例子**：`class DepartmentCreate(BaseModel): dept_code: str = Field(..., min_length=2)`。
> **什么时候用**：所有 POST/PUT 接口的请求体，以及需要控制返回字段的响应模型。

### 5.1.5 响应模型、HTTPException 与自动文档

**代码 5-1-6** · 响应模型与错误返回（Python）

```python
from fastapi import Depends, HTTPException
from pydantic import BaseModel

class DepartmentOut(BaseModel):
    id: int
    dept_code: str
    dept_name: str

@router.get("/{dept_id}", response_model=DepartmentOut)
def read_department(dept_id: int, db: dict = Depends(get_db)):
    if dept_id not in db:
        raise HTTPException(status_code=404, detail="部门不存在")
    return db[dept_id]
```

下面这段是机制示意，不是可直接运行的完整工程：`router` 来自 5.1.3 的 `APIRouter`，`get_db` 见 5.1.6 与 5.1.9 的 `deps.py`，完整可运行版本见 5.1.9。三个机制（`db` 参数的写法下一节讲）：

- `response_model=DepartmentOut`：返回值先过一遍输出模型，多出的字段会被滤掉。这解释了第 8 章“为什么 `password_hash` 不会漏出去”。
- `raise HTTPException(...)`：规则性失败提前返回，状态码与人话说明一起给出；而校验失败（422）不用手抛——Pydantic 在进入函数前就拦下了。
- 新增接口在装饰器里写 `status_code=201`，删除写 204。状态码是设计的一部分，不是运行时的运气。

自动接口文档：启动后访问 `/docs`，看到的接口、参数、返回结构全部从这些代码生成，代码一改文档即变——这就是第 4 章 4.1.9“代码是最终口径”的工具化落点。

> **补课卡 K-05 · HTTPException**
> **是什么**：FastAPI 的异常类，抛出时把状态码和说明一起返回给调用方。
> **为什么需要**：业务规则不满足（查无此部门、无权限）需要“提前结束请求并说清原因”，而不是让函数返回 `None`，也不是让异常变成 500。
> **最小例子**：`raise HTTPException(status_code=404, detail="部门不存在")`。
> **什么时候用**：所有“规则性失败”——404、401、403、400；校验类失败（422）交给 Pydantic，不用手抛。

### 5.1.6 Depends：把公共逻辑抽成参数

先忘记框架，看一个普通的 Python 问题：很多函数都需要先拿到“数据库”，于是每个函数的第一行都在重复 `db = 拿数据库()`。更好的做法是把“拿数据库”抽成一个函数，需要的人声明一下就行。FastAPI 把这个想法做成了语法：

**代码 5-1-7** · 依赖注入的最小对照（Python）

```python
from fastapi import Depends

def get_db():
    return {"D01": "一中队"}      # 公共逻辑只写一次（这里用字典假装数据库）

def list_departments(db=Depends(get_db)):    # 声明“我需要 get_db 的结果”
    return {"count": len(db)}                # 函数体只关心业务
```

`Depends(get_db)` 读作“给我 `get_db()` 的返回值”。框架在调用接口函数前先执行依赖，把结果塞进参数。三个推论：

1. 公共逻辑只写一次，改一处全体生效（比如给所有数据库会话加日志）。
2. 依赖可以叠依赖：`get_current_user` 内部又可以依赖“取令牌”，第 8 章会看到两层嵌套。
3. 测试时可以把依赖换成假的（不连真数据库）——这是第 14 章模块测试的钥匙。

> **补课卡 K-06 · Depends 与依赖注入**
> **是什么**：`Depends(函数)` 表示“调用接口前先执行这个函数，把返回值放进参数里”。
> **为什么需要**：拿数据库会话、解析令牌这类公共动作每个接口都要做；写成一处的依赖，接口函数只声明、不重复。
> **最小例子**：`def me(user = Depends(get_current_user)): return user`。
> **什么时候用**：第 8 章起高频出现。看到 `xxx = Depends(yyy)`，就读作“xxx 由 yyy 提供”。

### 5.1.7 Session、Base 与 get_db：数据库怎么接进来

实战代码（第 7 章起）里与数据库有关的三件套长这样：

**代码 5-1-8** · `app/core/database.py`（骨架；完整版见第 7 章《项目初始化与版本控制》的「从 `@app.get` 到 `@router.get`」一节，Python）

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

engine = create_engine("sqlite:///./duty.db")
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db          # 接口用完之后，才执行 finally 关闭会话
    finally:
        db.close()
```

三句话认识它们：`Base` 是所有表类的共同父类（第 9 章的表都继承它）；`Session` 是一次数据库会话，查询与写入都通过它；`get_db` 是把“开会话、用完关掉”包起来的依赖——所以后面章节的接口里总有一个 `db: Session = Depends(get_db)`。`yield` 的细节不影响使用，记住“依赖负责开关，接口只管用”即可。

SQL 一句话补课：`SELECT * FROM departments WHERE dept_code = 'D01'` 对应 `db.query(Department).filter(Department.dept_code == "D01")`。完整对照见附录 D《SQL 基础》。

> **补课卡 K-07 · ORM 与 SQLAlchemy**
> **是什么**：ORM（对象关系映射）把数据库表映射成 Python 类、行映射成对象；SQLAlchemy 是 Python 最常用的 ORM 之一。
> **为什么需要**：用 `db.query(Department)` 代替手写 SQL 字符串，字段名有代码提示，拼错会直接报错，而不是查出脏数据。
> **最小例子**：`Base` 是所有表类的父类；`Session` 是一次数据库会话，用完要关。
> **什么时候用**：第 7 章建库、第 10 章起的增删查改都建立在它上面；本章只需要认脸。

> **补课卡 K-08 · Optional 与 Literal**
> **是什么**：`Optional[int]` 表示“可以是 int，也可以是 None”；`Literal["admin", "normal"]` 表示“只能从这几个字符串里取值”。
> **为什么需要**：查询参数常有“不填就不过滤”的场景（`Optional`）；角色的合法取值是有限集合（`Literal`），写错在定义时就暴露。
> **最小例子**：`page_size: Optional[int] = None`；`role: Literal["admin", "normal"]`。
> **什么时候用**：第 8 章 8.1.6 起就会遇到（`Optional[dict]`），第 9 章账号管理、第 13 章统计校验会再用。**看不懂不影响往下做**——遇到时再回这张卡。

### 5.1.8 先导与回链：后面章节怎么用这些机制

先把本章的零件放回结构里看。下面这张表不引入新概念，只把已经见过的机制对应到它们在系统结构中的位置：

| 机制 | 在结构中的位置 | 第 6 章怎么用 |
| --- | --- | --- |
| `APIRouter` / `include_router` | 模块边界：一个业务模块一个 router | 6.1.3 模块划分、6.1.4 接口组 |
| Pydantic 输入 / 输出模型 | 模块的输入输出边界 | 6.1.2 表结构与接口字段、6.1.6 一致性 |
| `Depends` | 公共逻辑：认证、数据库会话等横切关注点 | 6.1.5 分层中的依赖 |
| `Session` / `get_db` | 数据访问 | 6.1.5 分层中的 crud |
| `HTTPException` | 错误边界 | 6.1.4 接口组的错误码 |

注意区分两组“层”：第 4 章的前端 / 后端 / 数据库是**部署三层**；第 6 章的 controller / service / crud / model 是**后端内部四层**。两者不是同一组层，不要混用。

本章讲的是“最小机制”。接下来几章会把它们用到真实场景，其中几个概念在这里只报到名字：

**表 5-1-1 · 先导与回链一览**

| 概念 | 本章只说了一句什么 | 完整展开 | 之后在哪反复用 |
| --- | --- | --- | --- |
| JWT 通行证 | 登录后发的带签名令牌 | 第 8 章 8.1.6 | 第 8、14、15 章 |
| passlib 密码哈希 | 存哈希不存明文 | 第 8 章 8.1.3 | 第 8 章 |
| 权限依赖 get_current_admin_user | 在认证之外再包一层 | 第 8 章 8.1.8 | 第 9 章 |
| ORM 建表与增删查改 | Base / Session / get_db 认脸 | 第 7 章建库、第 10 章增删查改 | 第 8–15 章 |
| SECRET_KEY / ALGORITHM | 签名密钥与算法放配置 | 第 7 章配置节、第 8 章 8.1.6 | 第 8 章 |
| TestClient 接口测试 | 不启动服务发起真实调用 | 第 4 章例 4-3、第 14 章 | 第 14 章 |

本书的规矩：**每一条“先导”都必须有回链落点**。你在后面任何一章遇到“似曾相识但没细讲”的符号，先回这张表；表里没有的，查附录 I《术语速查》。

### 5.1.9 本章完整最小工程（可运行全文）

把 5.1.2–5.1.6 的机制拼成一个能跑的完整工程：只有三个文件、约 70 行。纸上读代码建议按 `schemas.py` → `deps.py` → `main.py` 的顺序，与下面三个文件的排印顺序一致。

**代码 5-1-9** · `schemas.py`（全文，Python）

```python
from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    """新增部门的输入模型（第 8 章起你会反复见到这种写法）。"""
    dept_code: str = Field(..., min_length=2, max_length=10, examples=["D01"])
    dept_name: str = Field(..., min_length=2, max_length=50, examples=["一中队"])


class DepartmentOut(BaseModel):
    """返回给前端的输出模型：只有这三个字段，多一点都不给。"""
    id: int
    dept_code: str
    dept_name: str
```

**代码 5-1-10** · `deps.py`（全文，Python）

```python
from fastapi import Depends, HTTPException

# 用一个字典模拟数据库；第 10 章会把它换成真正的 SQLAlchemy 查询
FAKE_DB: dict[int, dict] = {
    1: {"id": 1, "dept_code": "D01", "dept_name": "一中队"},
    2: {"id": 2, "dept_code": "D02", "dept_name": "二中队"},
}


def get_db() -> dict:
    """公共依赖：所有需要访问“数据库”的路由都声明它。"""
    return FAKE_DB


def get_department_or_404(dept_id: int, db: dict = Depends(get_db)) -> dict:
    """公共依赖：按 id 取部门，取不到直接抛 404。"""
    if dept_id not in db:
        raise HTTPException(status_code=404, detail="部门不存在")
    return db[dept_id]
```

**代码 5-1-11** · `main.py`（全文，Python）

```python
from fastapi import APIRouter, Depends, FastAPI, status

from deps import get_db, get_department_or_404
from schemas import DepartmentCreate, DepartmentOut

router = APIRouter(prefix="/departments", tags=["部门"])


@router.get("", response_model=list[DepartmentOut])
def list_departments(db: dict = Depends(get_db)):
    """查询部门列表：GET + 集合资源。"""
    return sorted(db.values(), key=lambda d: d["id"])


@router.get("/{dept_id}", response_model=DepartmentOut)
def read_department(dept: dict = Depends(get_department_or_404)):
    """查询单个部门：路径参数定位资源，公共依赖处理 404。"""
    return dept


@router.post("", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(data: DepartmentCreate, db: dict = Depends(get_db)):
    """新增部门：请求体由 Pydantic 校验，失败返回 422。"""
    new_id = max(db) + 1
    record = {"id": new_id, **data.model_dump()}
    db[new_id] = record
    return record


@router.delete("/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    dept: dict = Depends(get_department_or_404),
    db: dict = Depends(get_db),
):
    """删除部门：成功返回 204，没有响应体。"""
    db.pop(dept["id"])


app = FastAPI(title="duty 最小工程", version="0.1.0")
app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
```

**表 5-1-2 · 最小工程文件清单**

| 文件 | 约行数 | 承担的机制 |
| --- | ---: | --- |
| `schemas.py` | 16 | 5.1.4 Pydantic 输入/输出模型 |
| `deps.py` | 22 | 5.1.5 HTTPException 与 5.1.6 Depends（含依赖叠依赖） |
| `main.py` | 42 | 5.1.2 路由、5.1.3 APIRouter 与 include_router |

**启动与自查**（在自己机器上）：

```text
$ pip install "fastapi[standard]"
$ uvicorn main:app --port 8000
→ 打开 http://127.0.0.1:8000/docs，能看到 5 个接口（4 个部门 + 1 个 health）
→ GET  /api/v1/departments 返回 200 与两条部门
→ POST /api/v1/departments 提交 {"dept_code":"D03","dept_name":"三中队"} 返回 201
→ POST /api/v1/departments 提交 {"dept_code":"D"} 返回 422（违反 min_length=2）
→ DELETE /api/v1/departments/999 返回 404
```

> 说明：`data.model_dump()` 是 Pydantic v2 的写法（把模型转成字典）；网上旧资料里的 `data.dict()` 是 v1 写法，两者不通用。装好 `fastapi[standard]` 后默认就是 v2。

读这套代码时对照三个问题：`router` 从哪来（`main.py` 顶部）；数据结构在哪约束（`schemas.py`）；公共逻辑在哪复用（`deps.py`）。这三个答案，就是第 7–15 章所有后端代码的地图。

## 5.2 示范例题

#### 例 5-1：读一段装饰器路由代码【Bloom：理解】

**题目**：下面的接口把 GET 请求绑定到一个函数。请指出方法、URL、参数位置与返回内容，并说明访问 `/departments/abc` 会发生什么、校验发生在哪一层。

```python
@app.get("/departments/{dept_id}")
def read_department(dept_id: int):
    return {"id": dept_id}
```

**解**：

1. 方法是 `GET`；URL 是 `/departments/{dept_id}`，表示查询单个部门。
2. `{dept_id}` 在路径里，是路径参数；`dept_id: int` 的类型注解要求它必须是整数。
3. 函数返回字典 `{"id": dept_id}`，FastAPI 自动转成 JSON；访问 `/departments/3` 得到 `{"id": 3}`，状态码 200。
4. 访问 `/departments/abc` 时，`abc` 无法解析为整数，返回 422，响应体 `detail` 中的 `type` 为 `int_parsing`。
5. 校验发生在进入函数体之前：FastAPI 读取类型注解，先做转换与校验，失败就直接返回 422，`read_department` 不会执行。

#### 例 5-2：把路由拆到 APIRouter 并挂载【Bloom：应用】

**题目**：为器材模块创建路由文件，提供 `GET /api/v1/devices`，返回空列表与总数 0；写出路由文件与 `main.py` 的挂载代码，并说明访问路径是怎么拼出来的。

**解**：

**代码 5-2-1** · `app/routers/devices.py`（路由模块，Python）

```python
from fastapi import APIRouter

router = APIRouter(prefix="/devices", tags=["器材"])

@router.get("")
def list_devices():
    return {"items": [], "total": 0}
```

**代码 5-2-2** · `main.py`（挂载，Python）

```python
from fastapi import FastAPI

from app.routers import devices

app = FastAPI()

app.include_router(devices.router, prefix="/api/v1")
```

1. `router` 由模块顶部的 `APIRouter(prefix="/devices")` 创建，`@router.get("")` 把列表接口登记到它上面。
2. `main.py` 的 `include_router(..., prefix="/api/v1")` 把模块路由挂进应用，两段前缀相加，最终路径是 `/api/v1/devices`。
3. `tags=["器材"]` 不影响 URL，只决定 `/docs` 里的分组名。
4. 启动后访问 `/docs`，能看到“器材”分组下的这个接口；调用 `GET /api/v1/devices` 返回 200 与 `{"items": [], "total": 0}`。

#### 例 5-3：用 Pydantic 模型接住请求体【Bloom：应用】

**题目**：为“新增器材”接口定义输入模型：`device_code` 必填、2–20 个字符；`device_name` 必填、2–50 个字符。写出模型与接口，并说明提交 `{"device_code": "E", "device_name": "投影仪"}` 时会发生什么。

**解**：

**代码 5-2-3** · `schemas.py`（输入模型，Python）

```python
from pydantic import BaseModel, Field


class DeviceCreate(BaseModel):
    device_code: str = Field(..., min_length=2, max_length=20)
    device_name: str = Field(..., min_length=2, max_length=50)
```

**代码 5-2-4** · `app/routers/devices.py`（新增接口，Python）

```python
@router.post("", status_code=201)
def create_device(data: DeviceCreate):
    return data
```

1. `DeviceCreate` 继承 `BaseModel`，两个字段的 `...` 表示必填，`min_length`、`max_length` 给出长度约束。
2. 接口参数写成 `data: DeviceCreate`，FastAPI 就知道“从请求体读 JSON，并按模型校验”。
3. 提交 `{"device_code": "E", "device_name": "投影仪"}` 时，`device_code` 只有 1 个字符，违反 `min_length=2`，返回 422。
4. `detail` 中 `loc` 指向 `["body", "device_code"]`，`type` 为 `string_too_short`，能定位到具体字段；校验在进入函数前完成，函数体不执行。
5. 合法请求返回 201；若用 `response_model` 声明输出模型，返回时还会按输出模型过滤字段——输入与输出必须分开定义。

## 5.3 独立习题

> 独立习题的参考答案统一放在书末第 98 章，做题时先不看。

#### 习题 5-1【Bloom：记忆】

**题目**：写出 FastAPI 的“四件核心机制”，并各写出一个对应的符号或写法：路由、数据、错误、复用。

#### 习题 5-2【Bloom：分析】

**题目**：同一条路径 `/square/{n}`，下面两个版本（分别部署）访问 `/square/abc` 时结果不同。请指出各自的状态码与原因，并说明类型注解在 FastAPI 里起什么作用。

```python
# 版本 A
@app.get("/square/{n}")
def square(n: int):
    return {"n": n, "square": n * n}

# 版本 B
@app.get("/square/{n}")
def square(n: str):
    return {"n": n, "square": n * n}
```

#### 习题 5-3【Bloom：分析】（综合：接口语义与机制）

**题目**：某同学的项目有三个问题：① 所有路由都写在 `main.py` 里；② 删除接口写成 `@app.post("/departments/delete/{dept_id}")`；③ 每个接口函数的第一行都是 `db = SessionLocal()`。请分别指出三处问题违背了第 4 章或本章的哪条规则，并用 `APIRouter`、`Depends` 与 RESTful 写法给出改造后的关键代码。

## ◇ 课堂活动块（课次 4 · 理论讲授）

**听讲要点**（课上跟着讲师过一遍，课后自查能否复述）：

1. FastAPI 的四件核心机制：路由（装饰器 + `APIRouter`）、数据（Pydantic 模型）、错误（`HTTPException`）、复用（`Depends`）。
2. 装饰器把“URL + 方法”登记到应用或路由上；类型注解让 FastAPI 在进入函数前完成转换与校验。
3. `APIRouter` 的“创建—挂载”链路：模块顶部 `APIRouter(...)`，`main.py` 用 `include_router` 组装。
4. 输入模型与输出模型必须分开；422 来自 Pydantic，404/401/403 等规则性失败来自 `HTTPException`。
5. `Depends` 把公共逻辑抽成参数；`get_db` 负责会话的开关。

**讨论·演示**：

1. （讨论）为什么输入模型与输出模型要分开定义？如果直接把数据库表模型当输出，`password_hash` 会怎样漏出去？
2. （演示）讲师启动 5.1.9 的最小工程，打开 `/docs`，依次调用查询、新增、删除接口，观察 200、201、204、404 与 422 各自的响应。

**课后自测**：完成独立习题 5-1～5-3（答案见书末《98-参考答案》）。其中 5-3 同时覆盖第 4 章的接口语义与本章机制，作为课次 4 的书面检查。

**回链**：本章 5.1.8 的回链表给出 JWT、ORM、TestClient 等概念的去向；第 7 章起，这些机制会在项目骨架与业务模块中逐个落地。

## 本章小结

**核心结论**：

1. FastAPI 的核心机制一共四件：**路由**（装饰器 + `APIRouter`）、**数据**（Pydantic 模型）、**错误**（`HTTPException`）、**复用**（`Depends`）。
2. 装饰器把“URL + 方法”与函数绑定；类型注解让框架在进入函数前完成转换与校验，校验失败返回 422。
3. `APIRouter` 把路由按模块拆分，`include_router` 把它们组装回应用；`router` 由模块顶部的 `APIRouter(...)` 创建。
4. Pydantic 用 `BaseModel` 与 `Field` 定义带约束的输入模型；输入与输出必须分开，输出模型负责过滤多余字段。
5. `Depends` 把公共逻辑抽成参数；`get_db` 用 `yield` 负责会话的开关，接口只声明、不重复。
6. 5.1.9 的最小工程三个文件是第 7–15 章代码的地图：`router` 从哪来、结构在哪约束、公共逻辑在哪复用。

**学完本章，你可以体会到**：这些机制不是“框架的花样”，而是把重复的登记、校验、开关会话从业务代码里拿走。认得出它们，后面几十个接口的代码就不再是黑箱。

**自检**：回到章首的学习目标，逐条问自己做到了没有——

- [ ] 用一句话说明 FastAPI 是什么、为什么选它 → 回看 5.1.1，自测：习题 5-1
- [ ] 解释装饰器路由与类型注解 → 回看 5.1.2、例 5-1，自测：习题 5-2
- [ ] 说出 `APIRouter` 与 `include_router` 的分工，指出 `router` 从哪来 → 回看 5.1.3、例 5-2，自测：习题 5-2
- [ ] 用 `BaseModel` 与 `Field` 定义输入模型，解释 422 产生在哪一层 → 回看 5.1.4、例 5-3，自测：习题 5-3
- [ ] 说明 `Depends` 与 `get_db` 的写法 → 回看 5.1.6、例 5-3，自测：习题 5-3
- [ ] 对照回链表说出 JWT、ORM 等概念的去向 → 回看 5.1.8，自测：习题 5-1

**下一章预告**：机制认全了，下一步是设计与建模——把需求变成表结构、模块划分与接口清单，再进入第 7 章的项目初始化。
