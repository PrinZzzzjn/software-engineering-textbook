from pydantic import BaseModel, Field


class PersonnelQueryParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    name: str | None = None
    dept_code: str | None = None
