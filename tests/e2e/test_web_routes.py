import pytest

@pytest.mark.e2e
class TestWebRoutes:
    async def test_home_page_returns_200_and_hero(self, async_client, mock_supabase):
        response = await async_client.get("/")
        assert response.status_code == 200
        assert "migrant" in response.text
        assert "Educação e Acolhimento" in response.text

    async def test_notices_catalog_page_returns_200(self, async_client, mock_supabase):
        response = await async_client.get("/editais?categoria=ensino_superior")
        assert response.status_code == 200
        assert "Catálogo de Editais" in response.text or "Oportunidades Oficiais" in response.text

    async def test_chat_page_returns_200(self, async_client):
        response = await async_client.get("/chat")
        assert response.status_code == 200
        assert "Assistente" in response.text and "migrantEU" in response.text

    async def test_confirm_subscription_magic_link(self, async_client, mock_supabase):
        response = await async_client.get("/subscribers/confirm/meu-token-magico-123")
        assert response.status_code == 200
        assert "Inscrição Confirmada" in response.text

    async def test_terms(self, async_client):
        r = await async_client.get("/termos-de-uso")
        assert r.status_code == 200

    async def test_privacy(self, async_client):
        r = await async_client.get("/privacidade")
        assert r.status_code == 200

    async def test_unsubscribe(self, async_client, mock_supabase):
        r = await async_client.get("/unsubscribe/test-token")
        assert r.status_code == 200

    async def test_communities(self, async_client, mock_supabase):
        r = await async_client.get("/comunidades")
        assert r.status_code == 200
