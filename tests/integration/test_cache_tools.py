import pytest
from unittest.mock import MagicMock
from app.ai.tools.check_cache import check_cached_notices_tool

@pytest.mark.integration
class TestCacheTool:
    async def test_cache_hit_locks_web_search(self, mock_supabase):
        # 1. Mock de busca de instituição
        # 2. Mock de busca de edital ativo
        mock_supabase["select"].side_effect = [
            MagicMock(data=[{"id": "inst-1", "name": "UFPR", "sigla": "UFPR", "official_domain": "ufpr.br"}]),
            MagicMock(data=[{
                "id": "notice-1",
                "title": "Vestibular CSVM",
                "category": "ensino_superior",
                "summary": "Vagas gratuitas para refugiados",
                "end_date": "2026-12-01",
                "notice_url": "https://ufpr.br/csvm"
            }])
        ]

        result = await check_cached_notices_tool.ainvoke({"institution": "UFPR", "category": "ensino_superior"})
        assert result["status"] == "CACHE_HIT"
        assert "NÃO realize busca externa" in result["message"]
        assert result["notice"]["title"] == "Vestibular CSVM"

    async def test_cache_miss_allows_search(self, mock_supabase):
        # Instituição não cadastrada ou sem edital vigente
        mock_supabase["select"].return_value = MagicMock(data=[])

        result = await check_cached_notices_tool.ainvoke({"institution": "InstituicaoSemEdital"})
        assert result["status"] == "CACHE_MISS"
        assert "Você está autorizado a buscar" in result["message"]
