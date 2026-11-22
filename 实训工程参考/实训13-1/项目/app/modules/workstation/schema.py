from pydantic import BaseModel, ConfigDict, Field


class WorkstationCreate(BaseModel):
    workstation_id: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    dept_code: str = Field(..., min_length=1, max_length=20)
    is_active: int = Field(default=1, ge=0, le=1)


class WorkstationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workstation_id: str
    name: str
    dept_code: str
    is_active: int


class WorkstationListOut(BaseModel):
    """列表响应统一为 {items, total}，由输出模型裁剪字段。"""

    items: list[WorkstationOut]
    total: int
