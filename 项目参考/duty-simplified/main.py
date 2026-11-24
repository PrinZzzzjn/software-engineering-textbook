from fastapi import FastAPI

from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.modules import department as department_module
from app.modules import duty_record as duty_record_module
from app.modules import personnel as personnel_module
from app.modules import user as user_module
from app.modules import workstation as workstation_module

from app.modules.analytics import controller as analytics_controller
from app.modules.department import controller as department_controller
from app.modules.duty_record import controller as duty_record_controller
from app.modules.personnel import controller as personnel_controller
from app.modules.user import controller as user_controller
from app.modules.workstation import controller as workstation_controller



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
# 建表前先导入所有模型，create_all 只识别已导入的模型
Base.metadata.create_all(bind=engine)

app = FastAPI(title="执勤电子年鉴")

app.include_router(user_controller.router)
app.include_router(department_controller.router)
app.include_router(personnel_controller.router)
app.include_router(workstation_controller.router)
app.include_router(duty_record_controller.router)
app.include_router(analytics_controller.router)


@app.get("/health")
def health():
    """服务级健康检查，供联调与容器探活使用。"""
    return {"status": "healthy"}


def _seed_demo_data():
    """写入一组教学演示数据；每条都先查存在性，重复启动不会重复写入。"""
    from datetime import datetime

    from app.modules.department.model import Department
    from app.modules.duty_record.model import DutyRecord
    from app.modules.personnel.model import Personnel
    from app.modules.user.model import User
    from app.modules.workstation.model import Workstation

    db = SessionLocal()
    try:
        # 演示账号：admin / admin123（role=admin）
        if not db.query(User).filter(User.username == "admin").first():
            db.add(
                User(
                    username="admin",
                    password_hash=get_password_hash("admin123"),
                    role="admin",
                    is_active=1,
                )
            )

        # 两个单位
        for code, name, addr in [
            ("D001", "一中队", "一号营区"),
            ("D002", "二中队", "二号营区"),
        ]:
            if not db.query(Department).filter(Department.dept_code == code).first():
                db.add(Department(dept_code=code, full_name=name, address=addr))

        # 两名人员
        for cert, name, code, rank in [
            ("P001", "张伟", "D001", "一级值班员"),
            ("P002", "李娜", "D002", "二级值班员"),
        ]:
            if (
                not db.query(Personnel)
                .filter(Personnel.certificate_number == cert)
                .first()
            ):
                db.add(
                    Personnel(
                        certificate_number=cert,
                        name=name,
                        dept_code=code,
                        rank=rank,
                    )
                )

        # 两个哨位
        for wid, name, code in [
            ("W001", "一号哨位", "D001"),
            ("W002", "二号哨位", "D002"),
        ]:
            if (
                not db.query(Workstation)
                .filter(Workstation.workstation_id == wid)
                .first()
            ):
                db.add(
                    Workstation(
                        workstation_id=wid, name=name, dept_code=code, is_active=1
                    )
                )

        # 若干执勤记录：集中在 2026 年，供统计页直接演示
        seed_records = [
            ("P001", "W001", datetime(2026, 3, 2, 8, 0), datetime(2026, 3, 2, 12, 0)),
            ("P001", "W001", datetime(2026, 3, 2, 13, 0), datetime(2026, 3, 2, 17, 0)),
            ("P001", "W001", datetime(2026, 4, 10, 8, 0), datetime(2026, 4, 10, 16, 0)),
            ("P002", "W002", datetime(2026, 3, 2, 8, 0), datetime(2026, 3, 2, 12, 0)),
        ]
        for cert, wid, start, end in seed_records:
            exists = (
                db.query(DutyRecord)
                .filter(
                    DutyRecord.personnel_certificate_number == cert,
                    DutyRecord.workstation_id == wid,
                    DutyRecord.start_time == start,
                )
                .first()
            )
            if not exists:
                db.add(
                    DutyRecord(
                        personnel_certificate_number=cert,
                        workstation_id=wid,
                        start_time=start,
                        end_time=end,
                        status="normal",
                    )
                )

        db.commit()
    finally:
        db.close()


_seed_demo_data()
