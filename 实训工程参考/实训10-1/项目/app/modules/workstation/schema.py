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
