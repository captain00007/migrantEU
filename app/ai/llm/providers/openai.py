from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.core.config import settings
from app.ai.llm.base import BaseLLMProvider, BaseEmbeddingsProvider

class OpenAILLMProvider(BaseLLMProvider):
    def create_llm(self, model_name: str | None = None, temperature: float = 0.2) -> BaseChatModel:
        model = model_name or settings.OPENAI_LLM_MODEL or "gpt-4o-mini"
        return ChatOpenAI(
            model=model,
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature
        )

class OpenAIEmbeddingsProvider(BaseEmbeddingsProvider):
    def create_embeddings(self, model_name: str | None = None, dimensions: int = 768) -> Embeddings:
        model = model_name or settings.OPENAI_EMBEDDING_MODEL or "text-embedding-3-small"
        return OpenAIEmbeddings(
            model=model,
            api_key=settings.OPENAI_API_KEY,
            dimensions=dimensions
        )
