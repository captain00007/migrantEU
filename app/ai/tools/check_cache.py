from typing import Optional, Literal
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app.ai.retrieval.cache_checker import CacheChecker

class CheckCacheInput(BaseModel):
    institution: str = Field(
        description="Nome ou sigla da instituição (ex: 'UFPR', 'USP', 'Cáritas', 'OIM', 'Unicamp')."
    )
    category: Optional[Literal["ensino_superior", "curso_portugues", "acolhimento_social", "pos_graduacao"]] = Field(
        default=None,
        description="Categoria opcional da oportunidade."
    )

@tool(args_schema=CheckCacheInput)
async def check_cached_notices_tool(institution: str, category: Optional[str] = None) -> dict:
    """
    ATENÇÃO: EXECUTE ESTA FERRAMENTA PRIMEIRO!
    Verifica se existe edital oficial vigente cadastrado no banco de dados para a instituição.
    Se o status retornado for 'CACHE_HIT', A BUSCA NA WEB ESTÁ ESTRITAMENTE TRAVADA:
    responda ao usuário com os dados de resumo, datas e link fornecidos aqui.
    """
    notice = await CacheChecker.check_active_notice(institution, category)
    if notice:
        return {
            "status": "CACHE_HIT",
            "message": "Edital vigente encontrado no banco de dados. NÃO realize busca externa.",
            "notice": {
                "id": notice["id"],
                "institution": notice.get("institution_name"),
                "sigla": notice.get("institution_sigla"),
                "title": notice["title"],
                "category": notice["category"],
                "summary": notice["summary"],
                "end_date": notice["end_date"],
                "notice_url": notice["notice_url"]
            }
        }
    return {
        "status": "CACHE_MISS",
        "message": "Nenhum edital vigente encontrado no banco. Você está autorizado a buscar em fontes oficiais seguras."
    }
