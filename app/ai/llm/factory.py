from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from app.core.config import settings
from app.ai.llm.providers.gemini import GeminiLLMProvider, GeminiEmbeddingsProvider
from app.ai.llm.providers.openai import OpenAILLMProvider, OpenAIEmbeddingsProvider
from app.ai.llm.providers.ollama import OllamaLLMProvider, OllamaEmbeddingsProvider

class LLMFactory:
    """
    Factory para instanciação dinâmica de LLMs seguindo SOLID (OCP e DIP).
    Suporta Google Gemini, OpenAI e Ollama local.
    """
    @classmethod
    def get_llm(
        cls,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2
    ) -> BaseChatModel:
        prov = (provider or settings.AI_LLM_PROVIDER).lower()
        if prov in ["google", "gemini"]:
            return GeminiLLMProvider().create_llm(model, temperature)
        elif prov == "openai":
            return OpenAILLMProvider().create_llm(model, temperature)
        elif prov in ["ollama", "llama"]:
            return OllamaLLMProvider().create_llm(model, temperature)
        else:
            raise ValueError(f"Provedor de LLM não suportado: {prov}")

class EmbeddingsFactory:
    """
    Factory para geradores de embeddings padronizados na dimensão unificada de 768 (compatível com Gemini, Ollama e OpenAI).
    """
    @classmethod
    def get_embeddings(
        cls,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        dimensions: Optional[int] = None
    ) -> Embeddings:
        prov = (provider or settings.AI_EMBEDDING_PROVIDER).lower()
        dims = dimensions or settings.AI_EMBEDDING_DIMENSIONS
        if prov in ["google", "gemini"]:
            return GeminiEmbeddingsProvider().create_embeddings(model, dims)
        elif prov == "openai":
            return OpenAIEmbeddingsProvider().create_embeddings(model, dims)
        elif prov in ["ollama", "llama"]:
            return OllamaEmbeddingsProvider().create_embeddings(model, dims)
        else:
            raise ValueError(f"Provedor de Embeddings não suportado: {prov}")
