import httpx
from app.ai.guardrails.domain_guard import DomainGuard

class WebLoader:
    """
    Carrega o conteúdo HTML de uma página web sob demanda via HTTP assíncrono.
    """
    @classmethod
    async def fetch_html(cls, url: str, extra_domain: str | None = None, timeout: float = 12.0) -> str:
        if not DomainGuard.is_url_allowed(url, extra_domain):
            raise PermissionError(f"A URL '{url}' não pertence aos domínios oficiais autorizados.")
        headers = {
            "User-Agent": "migrantEU-Bot/1.0 (+https://migranteu.org; Informações para Refugiados)"
        }
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
