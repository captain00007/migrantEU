import pytest
from app.ai.llm.factory import LLMFactory, EmbeddingsFactory

@pytest.mark.unit
class TestLLMFactory:
    def test_get_llm_unsupported_provider(self):
        with pytest.raises(ValueError, match="Provedor de LLM não suportado"):
            LLMFactory.get_llm(provider="desconhecido")

    def test_get_embeddings_unsupported_provider(self):
        with pytest.raises(ValueError, match="Provedor de Embeddings não suportado"):
            EmbeddingsFactory.get_embeddings(provider="desconhecido")

    def test_embeddings_dimensions_parameter(self, monkeypatch):
        # Garante que os embeddings são configurados com a dimensão unificada de 768
        from app.core.config import settings
        assert settings.AI_EMBEDDING_DIMENSIONS == 768
