"""
Authentication models for user management
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from bson import ObjectId

class UserSignup(BaseModel):
    """Signup request model"""
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    full_name: str

class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str
    user: UserResponse

class UserInDB(BaseModel):
    """User stored in database"""
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    email: str
    full_name: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True


