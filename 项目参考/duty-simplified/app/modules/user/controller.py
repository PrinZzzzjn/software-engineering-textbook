from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin_user, get_current_user
from app.modules.user import service
from app.modules.user.schema import (
    TokenOut,
    UserCreate,
    UserLogin,
    UserOut,
    UserPage,
    UserUpdate,
)
from app.modules.user.param import UserQueryParams

router = APIRouter(prefix="/users", tags=["用户"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return service.create_user(db, data)


@router.post("/login", response_model=TokenOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    access_token, user = service.authenticate(db, data)
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.get("", response_model=UserPage, dependencies=[Depends(get_current_admin_user)])
def list_users(
    params: UserQueryParams = Depends(),
    db: Session = Depends(get_db),
):
    return service.list_users(db, params)


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    return service.update_user(db, user_id, data, current_user)
