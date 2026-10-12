from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CommunityBase(BaseModel):
    name: str
    slug: str
    nationality_or_origin: str
    primary_language: Optional[str] = None
    uf: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    whatsapp_group_url: Optional[str] = None
    website_or_social_url: Optional[str] = None
    is_verified: bool = False
    is_active: bool = True

class CommunityCreate(CommunityBase):
    pass

class CommunityOut(CommunityBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
