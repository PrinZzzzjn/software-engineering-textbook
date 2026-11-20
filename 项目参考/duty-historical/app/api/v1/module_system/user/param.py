from pydantic import Field
from typing import Optional
from app.core.base_params import SearchParams
from app.api.v1.module_system.user.model import UserRole

class UserQueryParams(SearchParams):
    """用户查询参数"""
    username: Optional[str] = Field(default=None, description="用户名搜索")
    role: Optional[UserRole] = Field(default=None, description="角色筛选")
    is_active: Optional[int] = Field(default=None, ge=0, le=1, description="账号状态筛选(0:禁用,1:启用)")
    personnel_id: Optional[int] = Field(default=None, description="关联人员ID筛选")
