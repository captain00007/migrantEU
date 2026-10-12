import pytest

@pytest.mark.e2e
class TestAdminFlow:
    async def test_login_page_renders_form(self, async_client):
        response = await async_client.get("/admin/login")
        assert response.status_code == 200
        assert "Acesso Restrito" in response.text

    async def test_login_success_sets_session_cookie(self, async_client, mock_supabase):
        response = await async_client.post(
            "/admin/login",
            data={"email": "admin@migranteu.org", "password": "senhaCorretaSupabase123"},
            follow_redirects=False
        )
        assert response.status_code in [302, 303]
        assert "migranteu_admin_token" in response.cookies
        assert response.cookies["migranteu_admin_token"] == "valid-mock-supabase-token-xyz"

    async def test_login_failure_displays_error(self, async_client, mock_supabase):
        mock_supabase["auth_sign_in"].side_effect = Exception("Invalid login credentials")
        response = await async_client.post(
            "/admin/login",
            data={"email": "admin@migranteu.org", "password": "senhaIncorreta"},
            follow_redirects=False
        )
        assert response.status_code == 200
        assert "Credenciais inválidas" in response.text

    async def test_dashboard_requires_auth(self, async_client):
        response = await async_client.get("/admin/dashboard", follow_redirects=False)
        assert response.status_code in [302, 307]

    async def test_dashboard_authenticated_renders_content(self, async_client, admin_auth_token, mock_supabase):
        async_client.cookies.set("migranteu_admin_token", admin_auth_token)
        response = await async_client.get("/admin/dashboard")
        assert response.status_code == 200
        assert "Painel de Gestão e Moderação" in response.text

    async def test_update_ai_settings_endpoint(self, async_client, admin_auth_token, mock_supabase):
        async_client.cookies.set("migranteu_admin_token", admin_auth_token)
        data = {
            "llm_provider": "openai",
            "llm_model": "gpt-4o-mini"
        }
        response = await async_client.post("/admin/ai-settings", data=data, follow_redirects=False)
        assert response.status_code in [302, 303]

    async def test_logout_clears_cookie(self, async_client, admin_auth_token, mock_supabase):
        async_client.cookies.set("migranteu_admin_token", admin_auth_token)
        response = await async_client.get("/admin/logout", follow_redirects=False)
        assert response.status_code in [302, 303]
        # Cookie deve ser expirado ou removido
        cookie_header = response.headers.get("set-cookie", "")
        assert 'migranteu_admin_token=""' in cookie_header or "Max-Age=0" in cookie_header
