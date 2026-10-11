import io
import httpx
from pypdf import PdfReader
from app.ai.guardrails.domain_guard import DomainGuard

class PDFLoader:
    """
    Baixa e extrai texto de editais em formato PDF 100% em memória,
    sem persistir nenhum arquivo temporário no disco rígido.
    """
    @classmethod
    async def extract_text_from_url(cls, pdf_url: str, extra_domain: str | None = None, timeout: float = 20.0) -> str:
        if not DomainGuard.is_url_allowed(pdf_url, extra_domain):
            raise PermissionError(f"A URL do edital '{pdf_url}' não pertence a um domínio oficial autorizado.")
        headers = {
            "User-Agent": "migrantEU-Bot/1.0 (+https://migranteu.org)"
        }
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(pdf_url, headers=headers)
            response.raise_for_status()
            pdf_bytes = io.BytesIO(response.content)

        reader = PdfReader(pdf_bytes)
        extracted_text = []
        max_pages = min(len(reader.pages), 15)
        for i in range(max_pages):
            page_text = reader.pages[i].extract_text()
            if page_text:
                extracted_text.append(page_text)

        return chr(10).join(extracted_text)
