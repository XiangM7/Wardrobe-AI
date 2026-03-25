from datetime import datetime

from pydantic import EmailStr

from app.schemas.common import ORMModel


class UserCreate(ORMModel):
    name: str
    email: EmailStr


class UserUpdate(ORMModel):
    name: str
    email: EmailStr


class UserRead(ORMModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime


class UserSummary(ORMModel):
    id: int
    name: str
    email: EmailStr
