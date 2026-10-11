from datetime import date
from typing import List, Dict, Any, Optional
from app.core.database import SupabaseService
from app.services.email_service import EmailService

class NoticeService:
    """
    Regras de negócio para ciclo de vida de editais:
    - Listagem pública com cache
    - Aprovação Human-in-the-Loop com disparo de e-mails
    - Exclusão e expiração
    """
    @staticmethod
    async def list_active_notices(
        category: Optional[str] = None,
        uf: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        today_str = date.today().isoformat()

        def query(q):
            qb = q.select("*, institutions(name, sigla, uf, city, official_domain)").eq("status", "aprovado_vigente").gte("end_date", today_str)
            if category:
                qb = qb.eq("category", category)
            return qb.order("end_date", desc=False).limit(limit)

        res = await SupabaseService.table_select("notices", query)
        items = res.data or []
        for item in items:
            inst = item.get("institutions") or {}
            item["institution_name"] = inst.get("name")
            item["institution_sigla"] = inst.get("sigla")
            item["institution_uf"] = inst.get("uf")
            item["institution_city"] = inst.get("city")

        if uf:
            items = [i for i in items if (i.get("institution_uf") or "").upper() == uf.upper()]
        return items

    @staticmethod
    async def list_pending_notices() -> List[Dict[str, Any]]:
        def query(q):
            return q.select("*, institutions(name, sigla, uf, official_domain)").eq("status", "pendente_aprovacao").order("created_at", desc=True)

        res = await SupabaseService.table_select("notices", query)
        items = res.data or []
        for item in items:
            inst = item.get("institutions") or {}
            item["institution_name"] = inst.get("name")
            item["institution_sigla"] = inst.get("sigla")
            item["institution_uf"] = inst.get("uf")
        return items

    @staticmethod
    async def approve_notice(notice_id: str) -> Dict[str, Any]:
        # 1. Atualiza status para aprovado_vigente
        update_res = await SupabaseService.table_update("notices", "id", notice_id, {
            "status": "aprovado_vigente"
        })
        if not update_res.data:
            raise ValueError("Edital não encontrado para aprovação.")

        approved_notice = update_res.data[0]

        # 2. Busca dados completos da instituição
        inst_res = await SupabaseService.table_select("institutions", lambda q: q.select("*").eq("id", approved_notice["institution_id"]).limit(1))
        if inst_res.data:
            approved_notice["institution_name"] = inst_res.data[0]["name"]
            approved_notice["institution_sigla"] = inst_res.data[0]["sigla"]

        # 3. Busca assinantes interessados na categoria do edital
        category = approved_notice["category"]
        def query_subs(q):
            return q.select("email, topics, uf_preference").eq("is_active", True).contains("topics", [category])

        subs_res = await SupabaseService.table_select("subscribers", query_subs)
        subscribers = subs_res.data or []

        # 4. Dispara e-mails em lote via Resend
        sent_count = await EmailService.dispatch_notice_alert_batch(approved_notice, subscribers)

        return {
            "notice": approved_notice,
            "emails_dispatched": sent_count
        }

    @staticmethod
    async def reject_notice(notice_id: str) -> bool:
        res = await SupabaseService.table_delete("notices", "id", notice_id)
        return bool(res.data)

    @staticmethod
    async def expire_outdated_notices() -> int:
        today_str = date.today().isoformat()
        def query(q):
            return q.select("id").eq("status", "aprovado_vigente").lt("end_date", today_str)

        outdated_res = await SupabaseService.table_select("notices", query)
        outdated_ids = [item["id"] for item in (outdated_res.data or [])]
        
        count = 0
        for nid in outdated_ids:
            await SupabaseService.table_update("notices", "id", nid, {"status": "expirado"})
            count += 1
        return count
