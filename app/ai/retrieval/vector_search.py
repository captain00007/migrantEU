from typing import List, Dict, Any, Optional
from app.core.config import settings
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
        threshold: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        embeddings_model = EmbeddingsFactory.get_embeddings()
        query_vector = await embeddings_model.aembed_query(query)

        filter_category_id = category if (category and len(category) == 36 and "-" in category) else None
        filter_category_slug = category if (category and not filter_category_id) else None

        rpc_params = {
            "query_embedding": query_vector,
            "match_threshold": threshold if threshold is not None else settings.AI_VECTOR_THRESHOLD,
            "match_count": limit if limit is not None else settings.AI_VECTOR_LIMIT,
            "filter_category_id": filter_category_id,
            "filter_category_slug": filter_category_slug
        }
        res = await SupabaseService.rpc("match_notices", rpc_params)
        return res.data or []
