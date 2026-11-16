from typing import Literal, Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=50)


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    is_active: int


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    role: Optional[Literal["admin", "normal"]] = None
    is_active: Optional[Literal[0, 1]] = None
