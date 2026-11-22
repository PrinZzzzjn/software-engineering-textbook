from pydantic import BaseModel, Field


class DeptQuery(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
