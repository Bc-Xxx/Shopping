from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

VALID_ROLES = {"buyer", "seller"}


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "buyer"

    @field_validator("username")
    @classmethod
    def username_length(cls, v: str):
        if len(v) < 2 or len(v) > 50:
            raise ValueError("用户名长度 2-50")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str):
        if len(v) < 6:
            raise ValueError("密码至少 6 位")
        return v

    @field_validator("role")
    @classmethod
    def role_valid(cls, v: str):
        if v not in VALID_ROLES:
            raise ValueError(f"角色必须是 {', '.join(VALID_ROLES)}")
        return v


class UserOut(BaseModel):
    id: int
    username: str
    avatar: Optional[str] = None
    is_active: bool = True
    role: str = 'buyer'
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    token: str
    token_type: str = "bearer"
