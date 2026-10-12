from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app.services.community_service import CommunityService

class CommunitySearchInput(BaseModel):
    nationality: Optional[str] = Field(
        default=None,
        description="Nacionalidade ou origem da comunidade (ex: 'Haiti', 'Venezuela', 'Afeganistão', 'Congo', 'Síria')."
    )
    uf: Optional[str] = Field(
        default=None,
        description="Estado brasileiro de interesse (ex: 'PR', 'SP', 'RR', 'AM')."
    )

@tool(args_schema=CommunitySearchInput)
async def search_communities_tool(nationality: Optional[str] = None, uf: Optional[str] = None) -> dict:
    """
    Busca coletivos, associações e comunidades verificadas de apoio a migrantes e refugiados no Brasil.
    Use quando o usuário perguntar por grupos de apoio, associações de haitianos, venezuelanos ou de outras origens.
    """
    try:
        results = await CommunityService.list_communities(nationality=nationality, uf=uf, verified_only=False, limit=5)
        if results:
            clean = []
            for c in results:
                clean.append({
                    "name": c.get("name"),
                    "nationality_or_origin": c.get("nationality_or_origin"),
                    "primary_language": c.get("primary_language"),
                    "uf": c.get("uf"),
                    "city": c.get("city"),
                    "description": c.get("description"),
                    "contact_email": c.get("contact_email"),
                    "whatsapp_group_url": c.get("whatsapp_group_url"),
                    "website_or_social_url": c.get("website_or_social_url"),
                    "is_verified": c.get("is_verified")
                })
            return {
                "status": "SUCCESS",
                "count": len(clean),
                "communities": clean
            }
        return {
            "status": "NOT_FOUND",
            "message": "Nenhuma associação cadastrada especificamente para esses filtros, mas oriente a buscar a Pastoral do Migrante ou Cáritas local."
        }
    except Exception as e:
        return {"status": "ERROR", "message": f"Erro ao consultar comunidades: {str(e)}"}
