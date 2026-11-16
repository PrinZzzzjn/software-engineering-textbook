from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin_user, get_current_user
from app.modules.user import service
from app.modules.user.schema import LoginIn, TokenOut, UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["用户"])


@router.post("", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return service.create_user(db, data)


@router.post("/login", response_model=TokenOut)
def login_endpoint(data: LoginIn, db: Session = Depends(get_db)):
    return service.login(db, data)


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.get("", dependencies=[Depends(get_current_admin_user)])
def list_users(db: Session = Depends(get_db)):
    return service.list_users(db)


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    return service.update_user(db, user_id, data, current_user)
