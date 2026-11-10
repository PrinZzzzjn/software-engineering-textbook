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
