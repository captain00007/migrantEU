import pytest
from unittest.mock import MagicMock
from app.services.community_service import CommunityService
from app.ai.tools.check_communities import search_communities_tool

@pytest.mark.integration
class TestCommunityService:
    async def test_list_communities_filtering(self, mock_supabase):
        mock_supabase["select"].return_value = MagicMock(data=[
            {
                "id": "comm-1",
                "name": "Associação dos Haitianos de SP",
                "slug": "associacao-haitianos-sp",
                "nationality_or_origin": "Haiti",
                "primary_language": "Crioulo Haitiano",
                "uf": "SP",
                "city": "São Paulo",
                "is_verified": True
            }
        ])

        communities = await CommunityService.list_communities(nationality="Haiti", uf="SP")
        assert len(communities) == 1
        assert communities[0]["nationality_or_origin"] == "Haiti"
        assert communities[0]["is_verified"] is True

    async def test_search_communities_tool(self, mock_supabase):
        mock_supabase["select"].return_value = MagicMock(data=[
            {
                "id": "comm-2",
                "name": "Rede Venezuelana",
                "slug": "rede-venezuelana",
                "nationality_or_origin": "Venezuela",
                "primary_language": "Espanhol",
                "uf": "RR",
                "city": "Boa Vista",
                "is_verified": True,
                "whatsapp_group_url": "https://chat.whatsapp.com/exemplo"
            }
        ])

        result = await search_communities_tool.ainvoke({"nationality": "Venezuela", "uf": "RR"})
        assert result["status"] == "SUCCESS"
        assert result["count"] == 1
        assert result["communities"][0]["name"] == "Rede Venezuelana"
