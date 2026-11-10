from fastapi import Depends, HTTPException

# 用一个字典模拟数据库；第 10 章会把它换成真正的 SQLAlchemy 查询
FAKE_DB: dict[int, dict] = {
    1: {"id": 1, "dept_code": "D01", "dept_name": "一中队"},
    2: {"id": 2, "dept_code": "D02", "dept_name": "二中队"},
}


def get_db() -> dict:
    """公共依赖：所有需要访问“数据库”的路由都声明它。"""
    return FAKE_DB


def get_department_or_404(dept_id: int, db: dict = Depends(get_db)) -> dict:
    """公共依赖：按 id 取部门，取不到直接抛 404。"""
    if dept_id not in db:
        raise HTTPException(status_code=404, detail="部门不存在")
    return db[dept_id]
