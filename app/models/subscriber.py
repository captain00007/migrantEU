from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class SubscriberCreate(BaseModel):
    email: EmailStr
    topics: List[str] = []
    uf_preference: Optional[str] = None
    terms_consent: bool = True

class SubscriberOut(BaseModel):
    id: str
    email: EmailStr
    topics: List[str]
    uf_preference: Optional[str] = None
    magic_token: str
    is_active: bool
    consent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
