from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime

class ChatSessionCreate(BaseModel):
    session_token: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    is_active: bool = True

class ChatSessionOut(BaseModel):
    id: str
    session_token: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ChatMessageCreate(BaseModel):
    session_id: str
    role: str
    content: str
    reply_to: Optional[str] = None
    intent_key: Optional[str] = None
    metadata: Dict[str, Any] = {}

class ChatMessageOut(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    reply_to: Optional[str] = None
    intent_key: Optional[str] = None
    metadata: Dict[str, Any] = {}
    is_flagged: bool = False
    created_at: Optional[datetime] = None
