from fastapi import FastAPI

from app.core.database import Base, SessionLocal, engine
from app.modules.department import controller as department_controller
from app.modules.department import model as department_model  # noqa: F401  建表前先导入模型
from app.modules.personnel import controller as personnel_controller
from app.modules.personnel import model as personnel_model  # noqa: F401  建表前先导入模型
from app.modules.user import controller as user_controller
from app.modules.user import model as user_model  # noqa: F401  建表前先导入模型
from app.modules.user import service as user_service



def _load_case_data():
    """读取仓库统一案例数据；找不到时回落到本文件内置常量。"""
    import json
    from pathlib import Path
    candidates = [
        Path(__file__).resolve().parents[n] / "data" / "case_data.json"
        for n in range(1, 9)
    ]
    for candidate in candidates:
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
    return {}
app = FastAPI(title="Duty API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(department_controller.router, prefix="")
app.include_router(personnel_controller.router, prefix="")
app.include_router(user_controller.router, prefix="")

# 建表只创建缺失的表；表已存在时重复调用不会清空数据
Base.metadata.create_all(bind=engine)


def _seed_departments() -> None:
    """写入两个教学演示单位；逐条先查存在性，重复启动不会重复写入。"""
    db = SessionLocal()
    try:
        for code, name, address in [
            ("D001", "一中队", "一号营区"),
            ("D002", "二中队", "二号营区"),
        ]:
            exists = (
                db.query(department_model.Department)
                .filter(department_model.Department.dept_code == code)
                .first()
            )
            if not exists:
                db.add(
                    department_model.Department(
                        dept_code=code, full_name=name, address=address
                    )
                )
        db.commit()
    finally:
        db.close()


def _seed_personnel() -> None:
    """写入两个教学演示人员；所属单位由 _seed_departments 先写入。"""
    db = SessionLocal()
    try:
        for number, name, dept_code, rank in [
            ("P001", "张伟", "D001", "一级值班员"),
            ("P002", "李娜", "D002", "二级值班员"),
        ]:
            exists = (
                db.query(personnel_model.Personnel)
                .filter(personnel_model.Personnel.certificate_number == number)
                .first()
            )
            if not exists:
                db.add(
                    personnel_model.Personnel(
                        certificate_number=number,
                        name=name,
                        dept_code=dept_code,
                        rank=rank,
                    )
                )
        db.commit()
    finally:
        db.close()


def _seed_admin() -> None:
    """幂等写入 admin/admin123，供登录验收与第 9 章账号管理使用。"""
    db = SessionLocal()
    try:
        user_service.create_admin(db)
    finally:
        db.close()


_seed_departments()
_seed_personnel()
_seed_admin()
