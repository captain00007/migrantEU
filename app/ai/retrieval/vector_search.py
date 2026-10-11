from typing import List, Dict, Any, Optional
from app.core.database import SupabaseService
from app.ai.llm.factory import EmbeddingsFactory

class VectorSearch:
    """
    Realiza busca semântica por similaridade de cosseno usando a RPC 'match_notices' no Supabase pgvector.
    """
    @classmethod
    async def search_similar_notices(
        cls,
        query: str,
        category: Optional[str] = None,
        threshold: float = 0.60,
        limit: int = 4
    ) -> List[Dict[str, Any]]:
        embeddings_model = EmbeddingsFactory.get_embeddings()
        query_vector = await embeddings_model.aembed_query(query)

        rpc_params = {
            "query_embedding": query_vector,
            "match_threshold": threshold,
            "match_count": limit,
            "filter_category": category
        }
        res = await SupabaseService.rpc("match_notices", rpc_params)
        return res.data or []
