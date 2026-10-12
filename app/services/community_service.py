from typing import List, Dict, Any, Optional
from app.core.database import SupabaseService

class CommunityService:
    """
    Regras de negócio e consultas para coletivos e comunidades de apoio a migrantes.
    """
    @staticmethod
    async def list_communities(
        nationality: Optional[str] = None,
        uf: Optional[str] = None,
        verified_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        def query(q):
            qb = q.select("*").eq("is_active", True)
            if verified_only:
                qb = qb.eq("is_verified", True)
            if nationality:
                qb = qb.ilike("nationality_or_origin", f"%{nationality}%")
            if uf:
                qb = qb.eq("uf", uf.upper())
            return qb.order("name", desc=False).limit(limit)

        res = await SupabaseService.table_select("communities", query)
        return res.data or []

    @staticmethod
    async def get_community_by_slug(slug: str) -> Optional[Dict[str, Any]]:
        res = await SupabaseService.table_select("communities", lambda q: q.select("*").eq("slug", slug).limit(1))
        if res.data:
            return res.data[0]
        return None

    @staticmethod
    async def list_distinct_nationalities() -> List[str]:
        res = await SupabaseService.table_select("communities", lambda q: q.select("nationality_or_origin").eq("is_active", True))
        items = res.data or []
        nationalities = sorted(list({item["nationality_or_origin"] for item in items if item.get("nationality_or_origin")}))
        return nationalities
