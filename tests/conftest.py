import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from app.main import app

@pytest.fixture
def mock_supabase(monkeypatch):
    """
    Mock fixture para interceptar chamadas ao SupabaseService
    garantindo que os testes não façam I/O real no banco ou auth.
    """
    mock_select = AsyncMock()
    mock_insert = AsyncMock()
    mock_update = AsyncMock()
    mock_delete = AsyncMock()
    mock_rpc = AsyncMock()
    mock_auth_sign_in = AsyncMock()
    mock_auth_get_user = AsyncMock()
    mock_auth_sign_out = AsyncMock()

    # Respostas padrões
    mock_select.return_value = MagicMock(data=[])
    mock_insert.return_value = MagicMock(data=[{"id": "test-uuid-123"}])
    mock_update.return_value = MagicMock(data=[{"id": "test-uuid-123", "status": "aprovado_vigente"}])
    mock_delete.return_value = MagicMock(data=[{"id": "test-uuid-123"}])
    mock_rpc.return_value = MagicMock(data=[])

    # Mock Auth padrão
    mock_user = MagicMock()
    mock_user.id = "supabase-user-uuid-123"
    mock_user.email = "admin@migranteu.org"
    mock_user.user_metadata = {"role": "admin", "full_name": "Administrador migrantEU"}

    mock_session = MagicMock()
    mock_session.access_token = "valid-mock-supabase-token-xyz"

    mock_auth_response = MagicMock()
    mock_auth_response.user = mock_user
    mock_auth_response.session = mock_session

    mock_auth_sign_in.return_value = mock_auth_response
    mock_auth_get_user.return_value = MagicMock(user=mock_user)
    mock_auth_sign_out.return_value = None

    monkeypatch.setattr("app.core.database.SupabaseService.table_select", mock_select)
    monkeypatch.setattr("app.core.database.SupabaseService.table_insert", mock_insert)
    monkeypatch.setattr("app.core.database.SupabaseService.table_update", mock_update)
    monkeypatch.setattr("app.core.database.SupabaseService.table_delete", mock_delete)
    monkeypatch.setattr("app.core.database.SupabaseService.rpc", mock_rpc)
    monkeypatch.setattr("app.core.database.SupabaseService.auth_sign_in", mock_auth_sign_in)
    monkeypatch.setattr("app.core.database.SupabaseService.auth_get_user", mock_auth_get_user)
    monkeypatch.setattr("app.core.database.SupabaseService.auth_sign_out", mock_auth_sign_out)

    return {
        "select": mock_select,
        "insert": mock_insert,
        "update": mock_update,
        "delete": mock_delete,
        "rpc": mock_rpc,
        "auth_sign_in": mock_auth_sign_in,
        "auth_get_user": mock_auth_get_user,
        "auth_sign_out": mock_auth_sign_out
    }

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

@pytest.fixture
def admin_auth_token():
    return "valid-mock-supabase-token-xyz"
