"""内存版单位模型：用列表代替数据库表。

课堂统一使用单位示例。TABLE 先保留一条 D01，方便你看到数据；
阶段 2 会要求把它改成空列表，和完成态一致。
"""

from dataclasses import dataclass


@dataclass
class Department:
    dept_code: str
    full_name: str
    address: str | None = None


TABLE: list[Department] = [
    Department(dept_code="D01", full_name="一中队", address="一号楼"),
]
