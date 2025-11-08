"""
Authentication models for user management
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    @field_validator('created_at', 'last_login', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

