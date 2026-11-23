from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.user import service
from app.modules.user.schema import TokenOut, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/users", tags=["用户"])


@router.post("", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return service.create_user(db, data)


@router.post("/login", response_model=TokenOut)
def login_endpoint(data: UserLogin, db: Session = Depends(get_db)):
    return service.login(db, data)


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user
