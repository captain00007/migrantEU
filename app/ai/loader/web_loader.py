import httpx
from app.core.config import settings
from app.ai.guardrails.domain_guard import DomainGuard

class WebLoader:
    """
    Carrega o conteúdo HTML de uma página web sob demanda via HTTP assíncrono.
    """
    @classmethod
    async def fetch_html(cls, url: str, extra_domain: str | None = None, timeout: float | None = None) -> str:
        if not DomainGuard.is_url_allowed(url, extra_domain):
            raise PermissionError(f"A URL '{url}' não pertence aos domínios oficiais autorizados.")
        headers = {
            "User-Agent": settings.BOT_USER_AGENT
        }
        client_timeout = timeout if timeout is not None else settings.HTTP_TIMEOUT_SECONDS
        async with httpx.AsyncClient(timeout=client_timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
