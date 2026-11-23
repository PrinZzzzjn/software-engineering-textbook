from pydantic import BaseModel, Field


class UserQueryParams(BaseModel):
    """第 9 章用户列表的分页参数；本实训先按六文件体例占位，不挂列表路由。"""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
