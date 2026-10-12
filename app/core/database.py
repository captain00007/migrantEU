import asyncio
from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from app.core.config import settings

_supabase_client: Optional[Client] = None
_supabase_auth_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Retorna o cliente oficial Supabase com Service Role Key ou chave configurada para operações
    administrativas de banco de dados e vetores (pgvector).
    """
    global _supabase_client
    if _supabase_client is None:
        key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY or settings.SUPABASE_ANON_KEY
        if not settings.SUPABASE_URL or not key:
            print("[AVISO] Credenciais do Supabase não configuradas no .env.")
        _supabase_client = create_client(
            settings.SUPABASE_URL or "https://placeholder.supabase.co",
            key or "placeholder-key"
        )
    return _supabase_client

def get_supabase_auth_client() -> Client:
    """
    Retorna o cliente Supabase configurado para autenticação de usuários (auth.users).
    Utiliza anon_key, supabase_key ou service_role_key para interagir com a API de Auth.
    """
    global _supabase_auth_client
    if _supabase_auth_client is None:
        key = settings.SUPABASE_ANON_KEY or settings.SUPABASE_KEY or settings.SUPABASE_SERVICE_ROLE_KEY or "placeholder-key"
        _supabase_auth_client = create_client(
            settings.SUPABASE_URL or "https://placeholder.supabase.co",
            key
        )
    return _supabase_auth_client

class SupabaseService:
    """
    Camada de abstração assíncrona sobre o cliente Supabase,
    executando requisições em threadpool para não bloquear o loop de eventos do FastAPI.
    """
    @staticmethod
    async def table_select(table: str, query_fn) -> Any:
        client = get_supabase_client()
        def _execute():
            return query_fn(client.table(table)).execute()
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

    # =========================================================================
    # Métodos Nativos de Autenticação Supabase Auth (auth.users)
    # =========================================================================
    @staticmethod
    async def auth_sign_in(email: str, password: str) -> Any:
        auth_client = get_supabase_auth_client()
        def _execute():
            return auth_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
        return await asyncio.to_thread(_execute)

    @staticmethod
    async def auth_get_user(token: str) -> Any:
        auth_client = get_supabase_auth_client()
        def _execute():
            return auth_client.auth.get_user(token)
        return await asyncio.to_thread(_execute)

    @staticmethod
    async def auth_sign_out(token: str) -> Any:
        auth_client = get_supabase_auth_client()
        def _execute():
            try:
                return auth_client.auth.sign_out()
            except Exception:
                return None
        return await asyncio.to_thread(_execute)
