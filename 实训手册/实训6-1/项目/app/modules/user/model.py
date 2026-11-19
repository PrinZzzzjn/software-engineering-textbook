"""内存版用户数据：dataclass 描述字段，TABLE 充当“表”（教材 6.1）。"""

from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    role: str = "normal"
    is_active: int = 1


TABLE: list[User] = []
