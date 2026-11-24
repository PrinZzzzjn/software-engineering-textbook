from fastapi import FastAPI

from app.core.database import Base, SessionLocal, engine
from app.modules.department import controller as department_controller
from app.modules.department import model as department_model  # noqa: F401  建表前先导入模型



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


_seed_departments()
