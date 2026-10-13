import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.chat_service import ChatService

@pytest.mark.unit
class TestChatService:
    async def test_get_or_create_new_session(self, mock_supabase):
        mock_supabase["select"].return_value = MagicMock(data=[])
        mock_supabase["insert"].return_value = MagicMock(data=[{
            "id": "session-uuid-1",
            "session_token": "token-abc-123",
            "is_active": True
        }])

        session = await ChatService.get_or_create_session(
            session_token="token-abc-123",
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1"
        )
        assert session["id"] == "session-uuid-1"
        assert session["session_token"] == "token-abc-123"
        mock_supabase["insert"].assert_called_once()

    async def test_get_or_create_existing_session(self, mock_supabase):
        mock_supabase["select"].return_value = MagicMock(data=[{
            "id": "session-existing-99",
            "session_token": "token-existing",
            "is_active": True
        }])

        session = await ChatService.get_or_create_session(session_token="token-existing")
        assert session["id"] == "session-existing-99"
        mock_supabase["insert"].assert_not_called()

    async def test_save_user_message_has_no_reply_to(self, mock_supabase):
        mock_supabase["insert"].return_value = MagicMock(data=[{
            "id": "msg-user-1",
            "session_id": "session-1",
            "role": "user",
            "content": "Como me inscrever na UFPR?",
            "reply_to": None
        }])

        msg = await ChatService.save_user_message(
            session_id="session-1",
            content="Como me inscrever na UFPR?"
        )
        assert msg["role"] == "user"
        assert msg["reply_to"] is None
        assert msg["id"] == "msg-user-1"
        mock_supabase["insert"].assert_called_once()

    async def test_save_ai_message_sets_reply_to_user_message(self, mock_supabase):
        mock_supabase["insert"].return_value = MagicMock(data=[{
            "id": "msg-ai-1",
            "session_id": "session-1",
            "role": "assistant",
            "content": "A UFPR possui vestibular específico para refugiados.",
            "reply_to": "msg-user-1",
            "intent_key": "ensino_superior"
        }])

        msg = await ChatService.save_ai_message(
            session_id="session-1",
            content="A UFPR possui vestibular específico para refugiados.",
            reply_to="msg-user-1",
            intent_key="ensino_superior"
        )
        assert msg["role"] == "assistant"
        assert msg["reply_to"] == "msg-user-1"
        assert msg["intent_key"] == "ensino_superior"

    async def test_get_recent_history_chronological_order(self, mock_supabase):
        # O banco retorna ordenado por created_at desc (mais recente primeiro)
        # 10 mensagens = 5 perguntas + 5 respostas
        mock_data = [
            {"role": "assistant", "content": "Resposta 5", "created_at": "2026-10-12T12:09:00Z"},
            {"role": "user", "content": "Pergunta 5", "created_at": "2026-10-12T12:08:00Z"},
            {"role": "assistant", "content": "Resposta 4", "created_at": "2026-10-12T12:07:00Z"},
            {"role": "user", "content": "Pergunta 4", "created_at": "2026-10-12T12:06:00Z"},
            {"role": "assistant", "content": "Resposta 3", "created_at": "2026-10-12T12:05:00Z"},
            {"role": "user", "content": "Pergunta 3", "created_at": "2026-10-12T12:04:00Z"},
            {"role": "assistant", "content": "Resposta 2", "created_at": "2026-10-12T12:03:00Z"},
            {"role": "user", "content": "Pergunta 2", "created_at": "2026-10-12T12:02:00Z"},
            {"role": "assistant", "content": "Resposta 1", "created_at": "2026-10-12T12:01:00Z"},
            {"role": "user", "content": "Pergunta 1", "created_at": "2026-10-12T12:00:00Z"},
        ]
        mock_supabase["select"].return_value = MagicMock(data=mock_data)

        history = await ChatService.get_recent_history(session_id="session-1", limit=10)
        assert len(history) == 10
        # A ordem final deve ser cronológica crescente: Pergunta 1 até Resposta 5
        assert history[0]["content"] == "Pergunta 1"
        assert history[0]["role"] == "user"
        assert history[-1]["content"] == "Resposta 5"
        assert history[-1]["role"] == "assistant"
