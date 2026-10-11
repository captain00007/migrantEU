from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class SubscriberCreate(BaseModel):
    email: EmailStr
    topics: List[str] = []
    uf_preference: Optional[str] = None

class SubscriberOut(BaseModel):
    id: str
    email: EmailStr
    topics: List[str]
    uf_preference: Optional[str] = None
    magic_token: str
    is_active: bool
    created_at: Optional[datetime] = None
