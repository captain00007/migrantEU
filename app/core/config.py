import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "migrantEU"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "migranteu-insecure-change-me-in-production-secret-token"
    ALLOWED_HOSTS: str = "*"
    BASE_URL: str = "http://localhost:8000"

    # Supabase (Exclusivo para persistência e vetores)
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""

    # Switches Principais de IA
    AI_LLM_PROVIDER: str = "google"
    AI_LLM_MODEL: str = "gemini-1.5-flash"
    AI_EMBEDDING_PROVIDER: str = "google"
    AI_EMBEDDING_MODEL: str = "models/text-embedding-004"
    AI_EMBEDDING_DIMENSIONS: int = 768  # Dimensão unificada: 768 (Gemini, Ollama e OpenAI MRL)

    # 1. Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_LLM_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"

    # 2. OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_LLM_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # 3. Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_LLM_MODEL: str = "llama3:8b"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

    # Busca Web Segura
    TAVILY_API_KEY: str = ""

    # E-mails Transacionais
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "notificacoes@migranteu.org"

    # LangSmith / Observabilidade
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "migranteu"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
