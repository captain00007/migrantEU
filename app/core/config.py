import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # =========================================================================
    # Configurações Gerais do Servidor Web
    # =========================================================================
    APP_NAME: str = "migrantEU"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "migranteu-insecure-change-me-in-production-secret-token"
    ALLOWED_HOSTS: str = "*"
    BASE_URL: str = "http://localhost:8000"

    # =========================================================================
    # Conexão com Supabase (Persistência, Auth e pgvector)
    # =========================================================================
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # =========================================================================
    # Segurança de Sessão de Administração (Cookies)
    # =========================================================================
    ADMIN_SESSION_COOKIE_NAME: str = "migranteu_admin_token"
    ADMIN_SESSION_MAX_AGE_SECONDS: int = 86400  # 24 horas

    # =========================================================================
    # Limites de Listagem e Paginação de Editais
    # =========================================================================
    HOME_NOTICES_LIMIT: int = 6
    CATALOG_NOTICES_LIMIT: int = 50

    # =========================================================================
    # Agendador Diário (APScheduler)
    # =========================================================================
    SCHEDULER_CRON_HOUR: int = 0
    SCHEDULER_CRON_MINUTE: int = 5

    # =========================================================================
    # Robô de Coleta e Requisições HTTP
    # =========================================================================
    BOT_USER_AGENT: str = "migrantEU-Bot/1.0 (+https://migranteu.org; Informações para Refugiados)"
    HTTP_TIMEOUT_SECONDS: float = 12.0

    # =========================================================================
    # Switches Principais de Inteligência Artificial
    # =========================================================================
    AI_LLM_PROVIDER: str = "google"
    AI_LLM_MODEL: str = "gemini-1.5-flash"
    AI_EMBEDDING_PROVIDER: str = "google"
    AI_EMBEDDING_MODEL: str = "models/text-embedding-004"
    AI_EMBEDDING_DIMENSIONS: int = 768  # Dimensão unificada: 768 (Gemini, Ollama e OpenAI MRL)

    AI_TEMPERATURE: float = 0.2
    AI_AGENT_MAX_ITERATIONS: int = 4

    # =========================================================================
    # Busca Vetorial e Semântica (pgvector)
    # =========================================================================
    AI_VECTOR_THRESHOLD: float = 0.60
    AI_VECTOR_LIMIT: int = 4

    # =========================================================================
    # Leitor de Editais em Tempo Real (Live Reader)
    # =========================================================================
    AI_READER_MAX_CHARS: int = 4000

    # =========================================================================
    # Provedor: Google Gemini
    # =========================================================================
    GEMINI_API_KEY: str = ""
    GEMINI_LLM_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"

    # =========================================================================
    # Provedor: OpenAI
    # =========================================================================
    OPENAI_API_KEY: str = ""
    OPENAI_LLM_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # =========================================================================
    # Provedor: Ollama (100% Local)
    # =========================================================================
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_LLM_MODEL: str = "llama3:8b"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

    # =========================================================================
    # Busca Web Segura (Tavily)
    # =========================================================================
    TAVILY_API_KEY: str = ""
    AI_SEARCH_MAX_RESULTS: int = 3
    AI_SEARCH_DEPTH: str = "advanced"

    # =========================================================================
    # Guardrail de Domínios (Domínios extras customizados separados por vírgula)
    # =========================================================================
    DOMAIN_GUARD_CUSTOM_DOMAINS: str = ""

    # =========================================================================
    # E-mails Transacionais (Resend)
    # =========================================================================
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "notificacoes@migranteu.org"

    # =========================================================================
    # Observabilidade & Métricas (LangSmith)
    # =========================================================================
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
