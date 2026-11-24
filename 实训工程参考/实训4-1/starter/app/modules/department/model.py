"""内存版单位模型：用列表代替数据库表。字段按自选资源替换。"""

from dataclasses import dataclass


@dataclass
class Department:
    dept_code: str
    full_name: str
    address: str | None = None


TABLE: list[Department] = [
    Department(dept_code="D001", full_name="一中队", address="一号营区"),
]
