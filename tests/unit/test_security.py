import pytest
from app.core.security import verify_supabase_admin_token

@pytest.mark.unit
class TestSecurity:
    async def test_verify_supabase_admin_token_valid(self, mock_supabase):
        result = await verify_supabase_admin_token("valid-mock-token")
        assert result is not None
        assert result["id"] == "supabase-user-uuid-123"
        assert result["email"] == "admin@migranteu.org"
        assert result["role"] == "admin"
        assert result["full_name"] == "Administrador migrantEU"

    async def test_verify_supabase_admin_token_empty(self):
        result = await verify_supabase_admin_token("")
        assert result is None

    async def test_verify_supabase_admin_token_invalid(self, mock_supabase):
        mock_supabase["auth_get_user"].side_effect = Exception("Invalid token")
        result = await verify_supabase_admin_token("invalid-token")
        assert result is None
