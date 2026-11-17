"""内存版部门模型：用模块级列表代替数据库表，第 6 章换成 SQLAlchemy。"""

from dataclasses import dataclass


@dataclass
class Department:
    dept_code: str
    full_name: str
    address: str | None = None


TABLE: list[Department] = []
