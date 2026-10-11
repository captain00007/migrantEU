import asyncio
from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from app.core.config import settings

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    # Retorna o cliente oficial Supabase com Service Role Key
    global _supabase_client
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            print("[AVISO] Credenciais do Supabase não configuradas no .env. Inicializando em modo de espera.")
        _supabase_client = create_client(
            settings.SUPABASE_URL or "https://placeholder.supabase.co",
            settings.SUPABASE_SERVICE_ROLE_KEY or "placeholder-key"
        )
    return _supabase_client

class SupabaseService:
    # Camada de abstração assíncrona sobre o cliente Supabase
    @staticmethod
    async def table_select(table: str, query_fn) -> Any:
        client = get_supabase_client()
        def _execute():
            q = client.table(table)
            return query_fn(q).execute()
        return await asyncio.to_thread(_execute)

    @staticmethod
    async def table_insert(table: str, data: Dict[str, Any]) -> Any:
        client = get_supabase_client()
        def _execute():
            return client.table(table).insert(data).execute()
        return await asyncio.to_thread(_execute)

    @staticmethod
    async def table_update(table: str, match_col: str, match_val: Any, data: Dict[str, Any]) -> Any:
        client = get_supabase_client()
        def _execute():
            return client.table(table).update(data).eq(match_col, match_val).execute()
        return await asyncio.to_thread(_execute)

    @staticmethod
    async def table_delete(table: str, match_col: str, match_val: Any) -> Any:
        client = get_supabase_client()
        def _execute():
            return client.table(table).delete().eq(match_col, match_val).execute()
        return await asyncio.to_thread(_execute)

    @staticmethod
    async def rpc(function_name: str, params: Dict[str, Any]) -> Any:
        client = get_supabase_client()
        def _execute():
            return client.rpc(function_name, params).execute()
        return await asyncio.to_thread(_execute)
