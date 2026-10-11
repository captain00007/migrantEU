from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class InstitutionBase(BaseModel):
    name: str
    sigla: Optional[str] = None
    uf: str
    city: Optional[str] = None
    website_url: str
    official_domain: str
    is_active: bool = True

class InstitutionCreate(InstitutionBase):
    pass

class InstitutionOut(InstitutionBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
