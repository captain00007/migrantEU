import pytest
from unittest.mock import AsyncMock

@pytest.mark.e2e
class TestApiEndpoints:
    async def test_subscriber_registration_endpoint(self, async_client, mock_supabase):
        data = {
            "email": "refugiado.novo@exemplo.org",
            "topics": ["ensino_superior", "curso_portugues"],
            "uf_preference": "PR"
        }
        response = await async_client.post("/api/subscribers", data=data)
        assert response.status_code == 200
        assert "Inscrição Realizada com Sucesso" in response.text

    async def test_chat_message_endpoint_returns_html_bubbles(self, async_client, mock_supabase, monkeypatch):
        # Mock do process_chat_message para evitar consumo de tokens na IA externa
        monkeypatch.setattr(
            "app.routers.api.process_chat_message",
            AsyncMock(return_value="A UFPR oferece vestibular especial com isenção de taxa para refugiados.")
        )

        response = await async_client.post("/api/chat/message", data={"message": "Tem vestibular na UFPR?"})
        assert response.status_code == 200
        assert "Tem vestibular na UFPR?" in response.text
        assert "A UFPR oferece vestibular especial" in response.text
