from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from app.core.config import settings
from app.ai.llm.base import BaseLLMProvider, BaseEmbeddingsProvider

class OllamaLLMProvider(BaseLLMProvider):
    def create_llm(self, model_name: str | None = None, temperature: float = 0.2) -> BaseChatModel:
        model = model_name or settings.OLLAMA_LLM_MODEL or "llama3:8b"
        try:
            from langchain_ollama import ChatOllama
            return ChatOllama(
                base_url=settings.OLLAMA_BASE_URL,
                model=model,
                temperature=temperature
            )
        except ImportError:
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(
                base_url=settings.OLLAMA_BASE_URL,
                model=model,
                temperature=temperature
            )

class OllamaEmbeddingsProvider(BaseEmbeddingsProvider):
    def create_embeddings(self, model_name: str | None = None, dimensions: int = 768) -> Embeddings:
        model = model_name or settings.OLLAMA_EMBEDDING_MODEL or "nomic-embed-text"
        try:
            from langchain_ollama import OllamaEmbeddings
            return OllamaEmbeddings(
                base_url=settings.OLLAMA_BASE_URL,
                model=model
            )
        except ImportError:
            from langchain_community.embeddings.ollama import OllamaEmbeddings
            return OllamaEmbeddings(
                base_url=settings.OLLAMA_BASE_URL,
                model=model
            )
