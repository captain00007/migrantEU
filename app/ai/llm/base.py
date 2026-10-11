from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

class BaseLLMProvider(ABC):
    @abstractmethod
    def create_llm(self, model_name: str | None = None, temperature: float = 0.2) -> BaseChatModel:
        pass

class BaseEmbeddingsProvider(ABC):
    @abstractmethod
    def create_embeddings(self, model_name: str | None = None, dimensions: int = 768) -> Embeddings:
        pass
