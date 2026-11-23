from pydantic import BaseModel, Field


class UserQueryParams(BaseModel):
    """用户列表的分页参数，边界与第 7 章其它模块一致。"""

    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
