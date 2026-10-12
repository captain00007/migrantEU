import io
import httpx
from pypdf import PdfReader
from app.core.config import settings
from app.ai.guardrails.domain_guard import DomainGuard

class PDFLoader:
    """
    Extrai texto de arquivos PDF acadêmicos/governamentais sob demanda via stream na memória.
    """
    @classmethod
    async def extract_text_from_url(cls, url: str, extra_domain: str | None = None, timeout: float | None = None) -> str:
        if not DomainGuard.is_url_allowed(url, extra_domain):
            raise PermissionError(f"A URL do PDF '{url}' não pertence aos domínios autorizados.")
        headers = {
            "User-Agent": settings.BOT_USER_AGENT
        }
        client_timeout = timeout if timeout is not None else settings.HTTP_TIMEOUT_SECONDS
        async with httpx.AsyncClient(timeout=client_timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            pdf_bytes = io.BytesIO(response.content)

        reader = PdfReader(pdf_bytes)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)
