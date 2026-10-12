import pytest
from app.services.email_service import EmailService

@pytest.mark.integration
class TestEmailService:
    async def test_welcome_email_simulation_mode(self):
        # Sem chave configurada, deve simular e retornar True
        success = await EmailService.send_welcome_email("teste@migranteu.org", "token-uuid-123")
        assert success is True

    async def test_dispatch_empty_subscribers(self):
        count = await EmailService.dispatch_notice_alert_batch({"title": "Edital"}, [])
        assert count == 0
