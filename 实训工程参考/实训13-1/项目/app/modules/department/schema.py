from pydantic import BaseModel, ConfigDict, Field


class DepartmentCreate(BaseModel):
    dept_code: str = Field(..., min_length=1, max_length=20)
    full_name: str = Field(..., min_length=1, max_length=100)
    address: str | None = Field(default=None, max_length=500)


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dept_code: str
    full_name: str
    address: str | None


class DepartmentListOut(BaseModel):
    """列表响应统一为 {items, total}，由输出模型裁剪字段。"""

    items: list[DepartmentOut]
    total: int
