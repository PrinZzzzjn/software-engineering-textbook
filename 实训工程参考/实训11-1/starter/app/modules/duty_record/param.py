from pydantic import BaseModel, Field


class DutyRecordQueryParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    personnel_certificate_number: str | None = None
    workstation_id: str | None = None
