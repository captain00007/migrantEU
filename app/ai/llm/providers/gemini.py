from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from app.core.config import settings
from app.ai.llm.base import BaseLLMProvider, BaseEmbeddingsProvider

class GeminiLLMProvider(BaseLLMProvider):
    def create_llm(self, model_name: str | None = None, temperature: float = 0.2) -> BaseChatModel:
        model = model_name or settings.GEMINI_LLM_MODEL or "gemini-1.5-flash"
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=temperature
        )

class GeminiEmbeddingsProvider(BaseEmbeddingsProvider):
    def create_embeddings(self, model_name: str | None = None, dimensions: int = 768) -> Embeddings:
        model = model_name or settings.GEMINI_EMBEDDING_MODEL or "models/text-embedding-004"
        return GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=settings.GEMINI_API_KEY
        )
