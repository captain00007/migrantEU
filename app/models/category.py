from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CategoryBase(BaseModel):
    slug: str
    name: str
    description: Optional[str] = None
    badge_color: str = "blue"
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
