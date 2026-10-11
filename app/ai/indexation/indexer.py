from typing import Dict, Any, Optional
from app.core.database import SupabaseService
from app.ai.llm.factory import EmbeddingsFactory

class NoticeIndexer:
    """
    Gera representações vetoriais (embeddings 768d) e persiste novos editais no Supabase.
    """
    @classmethod
    async def index_notice(cls, notice_data: Dict[str, Any]) -> Dict[str, Any]:
        title = notice_data.get('title', '')
        summary = notice_data.get('summary', '')
        text_to_embed = f"{title}\n{summary}"
        embeddings_model = EmbeddingsFactory.get_embeddings()
        vector = await embeddings_model.aembed_query(text_to_embed)

        payload = {
            "institution_id": notice_data["institution_id"],
            "category": notice_data["category"],
            "title": notice_data["title"],
            "notice_url": notice_data["notice_url"],
            "start_date": notice_data.get("start_date"),
            "end_date": notice_data["end_date"],
            "summary": notice_data["summary"],
            "status": notice_data.get("status", "pendente_aprovacao"),
            "embedding": vector
        }
        res = await SupabaseService.table_insert("notices", payload)
        return res.data[0] if res.data else {}
