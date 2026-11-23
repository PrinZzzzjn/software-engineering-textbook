from dataclasses import dataclass


@dataclass
class Department:
    dept_code: str
    full_name: str
    address: str | None = None


TABLE: list[Department] = []
