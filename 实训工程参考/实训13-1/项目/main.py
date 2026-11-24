from datetime import datetime

from fastapi import FastAPI

from app.core.database import Base, SessionLocal, engine
from app.modules.analytics import controller as analytics_controller
from app.modules.department import controller as department_controller
from app.modules.department import model as department_model  # noqa: F401  建表前先导入模型
from app.modules.duty_record import controller as duty_record_controller
from app.modules.duty_record import model as duty_record_model  # noqa: F401  建表前先导入模型
from app.modules.personnel import controller as personnel_controller
from app.modules.personnel import model as personnel_model  # noqa: F401  建表前先导入模型
from app.modules.user import controller as user_controller
from app.modules.user import model as user_model  # noqa: F401  建表前先导入模型
from app.modules.user import service as user_service
from app.modules.workstation import controller as workstation_controller
from app.modules.workstation import model as workstation_model  # noqa: F401  建表前先导入模型



def _load_case_data():
    """读取仓库统一案例数据；找不到时回落到本文件内置常量。"""
    import json
    from pathlib import Path
    candidates = [
        Path(__file__).resolve().parents[n] / "data" / "case_data.json"
        for n in range(1, 6)
    ]
    for candidate in candidates:
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
    return {}


def _seed_rows(entities, keys, fallback):
    """从统一数据实体中取字段；数据缺失时用已同步的字面量。"""
    rows = []
    for entity in entities:
        fields = entity.get("fields", {})
        values = tuple(fields.get(key) for key in keys)
        if not all(value not in (None, "") for value in values):
            continue
        rows.append(
            dict(zip(keys, values)) if isinstance(fallback, dict)
            else values
        )
    return rows or fallback

DATA = _load_case_data()
app = FastAPI(title="Duty API", version="0.4.0")


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(department_controller.router, prefix="")
app.include_router(personnel_controller.router, prefix="")
app.include_router(workstation_controller.router, prefix="")
app.include_router(duty_record_controller.router, prefix="")
app.include_router(analytics_controller.router, prefix="")
app.include_router(user_controller.router, prefix="")

# 建表只创建缺失的表；表已存在时重复调用不会清空数据
Base.metadata.create_all(bind=engine)


def _seed_departments() -> None:
    """写入两个教学演示单位；逐条先查存在性，重复启动不会重复写入。"""
    db = SessionLocal()
    try:
        for code, name, address in _seed_rows(
            DATA.get("baseline", {}).get("departments", []),
            ("dept_code", "full_name", "address"),
            [("D001", "一中队", "一号营区"), ("D002", "二中队", "二号营区")],
        ):
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
        for number, name, dept_code, rank in _seed_rows(
            DATA.get("baseline", {}).get("personnel", []),
            ("certificate_number", "name", "dept_code", "rank"),
            [("P001", "张伟", "D001", "一级值班员"), ("P002", "李娜", "D002", "二级值班员")],
        ):
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


def _seed_workstations() -> None:
    """写入两个教学演示哨位；所属单位已由 _seed_departments 写入。"""
    db = SessionLocal()
    try:
        for workstation_id, name, dept_code in _seed_rows(
            DATA.get("baseline", {}).get("workstations", []),
            ("workstation_id", "name", "dept_code"),
            [("W001", "一号哨位", "D001"), ("W002", "二号哨位", "D002")],
        ):
            exists = (
                db.query(workstation_model.Workstation)
                .filter(
                    workstation_model.Workstation.workstation_id == workstation_id
                )
                .first()
            )
            if not exists:
                db.add(
                    workstation_model.Workstation(
                        workstation_id=workstation_id,
                        name=name,
                        dept_code=dept_code,
                        is_active=1,
                    )
                )
        db.commit()
    finally:
        db.close()


def _seed_duty_records() -> None:
    """写入四条互不重叠的执勤记录，供列表与第 11 章统计直接演示。

    这些记录直接经 ORM 写入，绕过接口校验；数据本身满足三条规则：
    开始早于结束、人员与哨位存在、同一哨位的时段不重叠。
    """
    db = SessionLocal()
    try:
        rows = [
            ("P001", "W001", datetime(2026, 3, 2, 8, 0), datetime(2026, 3, 2, 12, 0)),
            ("P001", "W001", datetime(2026, 3, 2, 13, 0), datetime(2026, 3, 2, 17, 0)),
            ("P001", "W001", datetime(2026, 4, 10, 8, 0), datetime(2026, 4, 10, 16, 0)),
            ("P002", "W002", datetime(2026, 3, 2, 8, 0), datetime(2026, 3, 2, 12, 0)),
        ]
        for cert, workstation_id, start, end in rows:
            exists = (
                db.query(duty_record_model.DutyRecord)
                .filter(
                    duty_record_model.DutyRecord.personnel_certificate_number == cert,
                    duty_record_model.DutyRecord.workstation_id == workstation_id,
                    duty_record_model.DutyRecord.start_time == start,
                )
                .first()
            )
            if not exists:
                db.add(
                    duty_record_model.DutyRecord(
                        personnel_certificate_number=cert,
                        workstation_id=workstation_id,
                        start_time=start,
                        end_time=end,
                        status="normal",
                    )
                )
        db.commit()
    finally:
        db.close()


def _seed_admin() -> None:
    """幂等写入 admin/admin123，供登录验收与账号管理使用。"""
    db = SessionLocal()
    try:
        user_service.create_admin(db)
    finally:
        db.close()


_seed_departments()
_seed_personnel()
_seed_workstations()
_seed_admin()
_seed_duty_records()
