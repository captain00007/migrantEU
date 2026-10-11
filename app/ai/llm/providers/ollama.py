from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from app.core.config import settings
from app.ai.llm.base import BaseLLMProvider, BaseEmbeddingsProvider

class OllamaLLMProvider(BaseLLMProvider):
    def create_llm(self, model_name: str | None = None, temperature: float = 0.2) -> BaseChatModel:
        model = model_name or settings.OLLAMA_LLM_MODEL or "llama3:8b"
        return ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=model,
            temperature=temperature
        )

class OllamaEmbeddingsProvider(BaseEmbeddingsProvider):
    def create_embeddings(self, model_name: str | None = None, dimensions: int = 768) -> Embeddings:
        model = model_name or settings.OLLAMA_EMBEDDING_MODEL or "nomic-embed-text"
        return OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model=model
        )
