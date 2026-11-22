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
