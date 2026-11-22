from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DutyRecordCreate(BaseModel):
    personnel_certificate_number: str = Field(..., min_length=1, max_length=20)
    workstation_id: str = Field(..., min_length=1, max_length=20)
    start_time: datetime
    end_time: datetime
    status: str = Field(default="normal", max_length=20)


class DutyRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    personnel_certificate_number: str
    workstation_id: str
    start_time: datetime
    end_time: datetime
    status: str


class DutyRecordListOut(BaseModel):
    """列表响应统一为 {items, total}，由输出模型裁剪字段。"""

    items: list[DutyRecordOut]
    total: int
