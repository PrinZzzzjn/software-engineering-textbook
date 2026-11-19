"""内存版单位模型：用模块级列表代替数据库表，第 8 章换成数据库版。"""

from dataclasses import dataclass


@dataclass
class Department:
    dept_code: str
    full_name: str
    address: str | None = None


TABLE: list[Department] = []
