"""工位模块的输入与输出模型（schema）：管什么能进、什么能出。

由第 4 章实训 4-1 的 schemas.py 迁入，内容不变，只是位置进入模块目录。
"""

from pydantic import BaseModel, Field


# 输入模型：新增时允许提交的字段与约束；校验失败由 Pydantic 返回 422。
class WorkstationCreate(BaseModel):
    workstation_id: str = Field(..., min_length=2, max_length=20)  # ... 表示必填
    workstation_name: str = Field(..., min_length=2, max_length=50)
    dept_code: str = Field(..., min_length=2, max_length=10)  # 外键：指向部门表
    # | None 表示可空；默认值 None 使其提交时可省略。
    category_code: str | None = None
    remark: str | None = None


# 输出模型：只声明允许出现在响应中的字段；接口声明 response_model 后按它过滤。
class WorkstationOut(BaseModel):
    workstation_id: str
    workstation_name: str
    dept_code: str
    category_code: str | None = None
    remark: str | None = None


# 列表输出：统一为 items 与 total，前端与后续分页都按这个结构取数。
class WorkstationListOut(BaseModel):
    items: list[WorkstationOut]
    total: int
