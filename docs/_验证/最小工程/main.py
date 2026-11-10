from fastapi import APIRouter, Depends, FastAPI, status

from deps import get_db, get_department_or_404
from schemas import DepartmentCreate, DepartmentOut

router = APIRouter(prefix="/departments", tags=["部门"])


@router.get("", response_model=list[DepartmentOut])
def list_departments(db: dict = Depends(get_db)):
    """查询部门列表：GET + 集合资源。"""
    return sorted(db.values(), key=lambda d: d["id"])


@router.get("/{dept_id}", response_model=DepartmentOut)
def read_department(dept: dict = Depends(get_department_or_404)):
    """查询单个部门：路径参数定位资源，公共依赖处理 404。"""
    return dept


@router.post("", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(data: DepartmentCreate, db: dict = Depends(get_db)):
    """新增部门：请求体由 Pydantic 校验，失败返回 422。"""
    new_id = max(db) + 1
    record = {"id": new_id, **data.model_dump()}
    db[new_id] = record
    return record


@router.delete("/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    dept: dict = Depends(get_department_or_404),
    db: dict = Depends(get_db),
):
    """删除部门：成功返回 204，没有响应体。"""
    db.pop(dept["id"])


app = FastAPI(title="duty 最小工程", version="0.1.0")
app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
