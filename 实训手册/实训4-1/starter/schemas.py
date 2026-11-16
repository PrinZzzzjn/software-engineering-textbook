"""综合实训 4-1 骨架：输入模型与输出模型（示例模块：工位）。

案例背景：执勤电子年鉴。部门下设工位，一个工位只属于一个部门；工位是值班安排的落点。
字段取自项目参考 duty 的工位表（workstation_id / workstation_name / dept_code /
category_code / remark）；实际项目另有自增 id 作物理主键，本实训按 4.2 的做法以业务编号作主键。

对应教材：第 3 章 3.5（Pydantic 输入模型、输出模型与 response_model）、
          第 4 章 4.5（schema.py 的职责：管什么能进、什么能出）。

本文件只放模型，不放接口逻辑。
提交时把示例模块替换为自己选定的业务对象（工位 / 器材 / 课程 / 图书）。
"""

from pydantic import BaseModel, Field


# 输入模型：调用方能提交哪些字段、各自受什么约束。校验失败由 Pydantic 在进入函数前返回 422。
class WorkstationCreate(BaseModel):
    """新增工位的输入模型：只包含调用方可以提交的字段。"""

    workstation_id: str = Field(
        ...,  # 省略号表示必填，没有默认值
        min_length=2,
        max_length=20,
        examples=["WS-001"],
        description="工位编号，唯一，本实训中作为主键",
    )
    workstation_name: str = Field(
        ..., min_length=2, max_length=50, examples=["一号值班台"], description="工位名称"
    )
    dept_code: str = Field(
        ..., min_length=2, max_length=10, examples=["D01"], description="所属部门内码，外键"
    )
    # | None 表示可空；Field 的默认值 None 使该字段提交时可省略。
    category_code: str | None = Field(None, max_length=20, description="工位类别内码，可选")
    remark: str | None = Field(None, max_length=200, description="备注，可选")


# 输出模型：只声明允许出现在响应中的字段；接口声明 response_model 后按它过滤。
class WorkstationOut(BaseModel):
    """单个工位的输出模型：决定哪些字段可以出现在响应中。"""

    workstation_id: str
    workstation_name: str
    dept_code: str
    category_code: str | None = None
    remark: str | None = None


# 列表输出：按 4.4 的约定统一为 items 与 total，前端与后续分页都按此结构取数。
class WorkstationListOut(BaseModel):
    """列表输出模型：按第 4 章 4.4 的跨模块约定，统一为 items 与 total。"""

    items: list[WorkstationOut]
    total: int
