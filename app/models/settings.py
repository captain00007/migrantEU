from typing import Optional, Dict, Any
from pydantic import BaseModel

class AISettingsSchema(BaseModel):
    llm_provider: str = "google"
    llm_model: str = "gemini-1.5-flash"
    embedding_provider: str = "google"
    embedding_model: str = "models/text-embedding-004"
    embedding_dimensions: int = 768

class SystemSettingUpdate(BaseModel):
    value: Dict[str, Any]
