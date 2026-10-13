import os
from typing import Optional
from dotenv import load_dotenv

# Carrega o arquivo .env para as variáveis de ambiente
load_dotenv(override=True)

class Settings:
    # =========================================================================
    # Configurações Gerais do Servidor Web
    # =========================================================================
    APP_NAME: str = os.getenv("APP_NAME", "migrantEU")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "migranteu-insecure-change-me-in-production-secret-token")
    ALLOWED_HOSTS: str = os.getenv("ALLOWED_HOSTS", "*")
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    # =========================================================================
    # Conexão com Supabase (Persistência, Auth e pgvector)
    # =========================================================================
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    # =========================================================================
    # Segurança de Sessão de Administração (Cookies)
    # =========================================================================
    ADMIN_SESSION_COOKIE_NAME: str = os.getenv("ADMIN_SESSION_COOKIE_NAME", "migranteu_admin_token")
    ADMIN_SESSION_MAX_AGE_SECONDS: int = int(os.getenv("ADMIN_SESSION_MAX_AGE_SECONDS", "86400"))

    # =========================================================================
    # Limites de Listagem e Paginação de Editais
    # =========================================================================
    HOME_NOTICES_LIMIT: int = int(os.getenv("HOME_NOTICES_LIMIT", "6"))
    CATALOG_NOTICES_LIMIT: int = int(os.getenv("CATALOG_NOTICES_LIMIT", "50"))

    # =========================================================================
    # Agendador Diário (APScheduler)
    # =========================================================================
    SCHEDULER_CRON_HOUR: int = int(os.getenv("SCHEDULER_CRON_HOUR", "0"))
    SCHEDULER_CRON_MINUTE: int = int(os.getenv("SCHEDULER_CRON_MINUTE", "5"))

    # =========================================================================
    # Robô de Coleta e Requisições HTTP
    # =========================================================================
    BOT_USER_AGENT: str = os.getenv("BOT_USER_AGENT", "migrantEU-Bot/1.0 (+https://migranteu.org; Informações para Refugiados)")
    HTTP_TIMEOUT_SECONDS: float = float(os.getenv("HTTP_TIMEOUT_SECONDS", "12.0"))

    # =========================================================================
    # Switches Principais de Inteligência Artificial
    # =========================================================================
    AI_LLM_PROVIDER: str = os.getenv("AI_LLM_PROVIDER", "openai")
    AI_LLM_MODEL: str = os.getenv("AI_LLM_MODEL", "gpt-4o-mini")
    AI_EMBEDDING_PROVIDER: str = os.getenv("AI_EMBEDDING_PROVIDER", "openai")
    AI_EMBEDDING_MODEL: str = os.getenv("AI_EMBEDDING_MODEL", "text-embedding-3-small")
    AI_EMBEDDING_DIMENSIONS: int = int(os.getenv("AI_EMBEDDING_DIMENSIONS", "768"))

    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.2"))
    AI_AGENT_MAX_ITERATIONS: int = int(os.getenv("AI_AGENT_MAX_ITERATIONS", "4"))

    # =========================================================================
    # Busca Vetorial e Semântica (pgvector)
    # =========================================================================
    AI_VECTOR_THRESHOLD: float = float(os.getenv("AI_VECTOR_THRESHOLD", "0.60"))
    AI_VECTOR_LIMIT: int = int(os.getenv("AI_VECTOR_LIMIT", "4"))

    # =========================================================================
    # Leitor de Editais em Tempo Real (Live Reader)
    # =========================================================================
    AI_READER_MAX_CHARS: int = int(os.getenv("AI_READER_MAX_CHARS", "4000"))

    # =========================================================================
    # Provedor: Google Gemini
    # =========================================================================
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_LLM_MODEL: str = os.getenv("GEMINI_LLM_MODEL", "gemini-flash-latest")
    GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")

    # =========================================================================
    # Provedor: OpenAI
    # =========================================================================
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_LLM_MODEL: str = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    # =========================================================================
    # Provedor: Ollama (100% Local)
    # =========================================================================
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_LLM_MODEL: str = os.getenv("OLLAMA_LLM_MODEL", "llama3:8b")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    # =========================================================================
    # Busca Web Segura (Tavily)
    # =========================================================================
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    AI_SEARCH_MAX_RESULTS: int = int(os.getenv("AI_SEARCH_MAX_RESULTS", "3"))
    AI_SEARCH_DEPTH: str = os.getenv("AI_SEARCH_DEPTH", "advanced")

    # =========================================================================
    # Guardrail de Domínios
    # =========================================================================
    DOMAIN_GUARD_CUSTOM_DOMAINS: str = os.getenv("DOMAIN_GUARD_CUSTOM_DOMAINS", "")

    # =========================================================================
    # E-mails Transacionais (Resend)
    # =========================================================================
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    RESEND_FROM_EMAIL: str = os.getenv("RESEND_FROM_EMAIL", "notificacoes@migranteu.org")

    # =========================================================================
    # Observabilidade & Métricas (LangSmith)
    # =========================================================================
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() in ("true", "1", "yes")
    LANGCHAIN_ENDPOINT: str = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "migrantia")

settings = Settings()

# Propaga configurações de rastreamento do LangSmith diretamente para os.environ
if settings.LANGCHAIN_TRACING_V2:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
    if settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
