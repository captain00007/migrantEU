from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "moderador"
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str
    hashed_password: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserOut(UserBase):
    id: str
    created_at: Optional[datetime] = None
