from pydantic import BaseModel, ConfigDict, Field


class PersonnelCreate(BaseModel):
    certificate_number: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    dept_code: str = Field(..., min_length=1, max_length=20)
    rank: str | None = Field(default=None, max_length=50)


class PersonnelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    certificate_number: str
    name: str
    dept_code: str
    rank: str | None


class PersonnelListOut(BaseModel):
    """列表响应统一为 {items, total}，由输出模型裁剪字段。"""

    items: list[PersonnelOut]
    total: int
