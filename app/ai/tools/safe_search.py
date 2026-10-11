from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from tavily import TavilyClient
from app.core.config import settings
from app.ai.guardrails.domain_guard import DomainGuard

class SafeSearchInput(BaseModel):
    query: str = Field(
        description="Termos de busca específicos para encontrar oportunidades ou editais (ex: 'vestibular refugiados UFPR edital 2026')."
    )
    institution_domain: Optional[str] = Field(
        default=None,
        description="Domínio oficial da instituição (ex: 'ufpr.br')."
    )

@tool(args_schema=SafeSearchInput)
async def safe_web_search_tool(query: str, institution_domain: Optional[str] = None) -> dict:
    """
    Executa busca segura na web usando Tavily com filtro obrigatório para domínios governamentais,
    universidades oficiais e organizações humanitárias autorizadas.
    Executada SOMENTE após confirmação de CACHE_MISS.
    """
    if not settings.TAVILY_API_KEY:
        return {
            "status": "ERROR",
            "message": "Chave da API Tavily não configurada. Não é possível realizar busca externa no momento."
        }

    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    domains = list(DomainGuard.OFFICIAL_DOMAINS_WHITELIST)
    if institution_domain:
        domains.append(institution_domain)

    search_query = f"{query} (migrantes OR refugiados OR acolhimento)"
    try:
        response = client.search(
            query=search_query,
            search_depth="advanced",
            include_domains=domains,
            max_results=3
        )
        filtered = []
        for r in response.get("results", []):
            url = r.get("url", "")
            if DomainGuard.is_url_allowed(url, institution_domain):
                filtered.append({
                    "title": r.get("title"),
                    "url": url,
                    "content": r.get("content")
                })
        return {
            "status": "SEARCH_SUCCESS",
            "results": filtered,
            "instruction": "Caso identifique um novo edital, informe que ele está em análise preliminar e use os links oficiais encontrados."
        }
    except Exception as e:
        return {"status": "ERROR", "message": f"Falha na busca web: {str(e)}"}
