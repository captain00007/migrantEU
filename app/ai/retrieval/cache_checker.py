from datetime import date
from typing import Optional, Dict, Any
from app.core.database import SupabaseService

class CacheChecker:
    """
    Executa a verificação no Supabase para aplicar a regra de cache do negócio:
    Se a instituição já possui edital vigente na categoria pesquisada,
    a busca externa na web é CONGELADA.
    """
    @classmethod
    async def check_active_notice(
        cls,
        institution_identifier: str,
        category: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        # 1. Localiza a instituição por sigla ou nome aproximado
        today_str = date.today().isoformat()
        
        def find_institution(q):
            return q.select("id, name, sigla, official_domain").or_(
                f"sigla.ilike.%{institution_identifier}%,name.ilike.%{institution_identifier}%"
            ).eq("is_active", True).limit(1)

        inst_res = await SupabaseService.table_select("institutions", find_institution)
        if not inst_res.data:
            return None

        institution = inst_res.data[0]
        inst_id = institution["id"]

        # 2. Busca edital vigente com status aprovado_vigente e end_date >= hoje
        def find_notice(q):
            query = q.select("*, categories(id, slug, name)").eq("institution_id", inst_id).eq("status", "aprovado_vigente").gte("end_date", today_str)
            if category:
                if len(category) == 36 and "-" in category:
                    query = query.eq("category_id", category)
                else:
                    query = query.eq("categories.slug", category)
            return query.order("end_date", desc=True).limit(1)

        notice_res = await SupabaseService.table_select("notices", find_notice)
        if notice_res.data:
            notice = notice_res.data[0]
            cat = notice.get("categories") or {}
            notice["institution_name"] = institution["name"]
            notice["institution_sigla"] = institution["sigla"]
            notice["official_domain"] = institution["official_domain"]
            notice["category_slug"] = cat.get("slug")
            notice["category_name"] = cat.get("name")
            notice["category"] = notice.get("category") or cat.get("slug")
            return notice

        return None
