from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime

class NoticeBase(BaseModel):
    institution_id: str
    category_id: Optional[str] = None
    category: Optional[str] = None  # Slug para compatibilidade
    category_slug: Optional[str] = None
    category_name: Optional[str] = None
    category_badge_color: Optional[str] = None
    title: str
    notice_url: str
    start_date: Optional[date] = None
    end_date: date
    summary: str
    status: str = "pendente_aprovacao"

class NoticeCreate(NoticeBase):
    embedding: Optional[List[float]] = None

class NoticeOut(NoticeBase):
    id: str
    institution_name: Optional[str] = None
    institution_sigla: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
