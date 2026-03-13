from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreateAdmin(UserBase):
    password: str
    is_admin: bool = False


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
