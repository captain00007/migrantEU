import uuid
from typing import List, Dict, Any, Optional
from app.core.database import SupabaseService

class ChatService:
    """
    Serviço de gerenciamento de sessões e histórico de mensagens do assistente migrantEU.
    Garante persistência de contexto do usuário e encadeamento de respostas via reply_to.
    """

    @staticmethod
    async def get_or_create_session(
        session_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Localiza uma sessão existente pelo token único de sessão ou registra uma nova sessão.
        """
        if not session_token:
            session_token = str(uuid.uuid4())

        try:
            res = await SupabaseService.table_select(
                "chat_sessions",
                lambda q: q.select("*").eq("session_token", session_token).limit(1)
            )
            if res and getattr(res, "data", None) and len(res.data) > 0:
                return res.data[0]

            new_session_id = str(uuid.uuid4())
            session_payload = {
                "id": new_session_id,
                "session_token": session_token,
                "user_agent": user_agent[:500] if user_agent else None,
                "ip_address": ip_address[:45] if ip_address else None,
                "is_active": True
            }
            insert_res = await SupabaseService.table_insert("chat_sessions", session_payload)
            if insert_res and getattr(insert_res, "data", None) and len(insert_res.data) > 0:
                return insert_res.data[0]
            return session_payload
        except Exception as e:
            print(f"[AVISO CHAT_SERVICE] Falha ao consultar/criar sessão no Supabase: {e}")
            return {"id": session_token, "session_token": session_token, "is_active": True}

    @staticmethod
    async def save_user_message(
        session_id: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Registra a mensagem enviada pelo usuário no histórico.
        reply_to permanece None para mensagens originadas pelo usuário.
        """
        msg_id = str(uuid.uuid4())
        payload = {
            "id": msg_id,
            "session_id": session_id,
            "role": "user",
            "content": content,
            "reply_to": None
        }
        try:
            res = await SupabaseService.table_insert("chat_messages", payload)
            if res and getattr(res, "data", None) and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            print(f"[AVISO CHAT_SERVICE] Falha ao persistir mensagem do usuário: {e}")
        return payload

    @staticmethod
    async def save_ai_message(
        session_id: str,
        content: str,
        reply_to: Optional[str] = None,
        intent_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Registra a resposta gerada pela IA, vinculando-a à mensagem do usuário
        através da chave estrangeira reply_to.
        """
        msg_id = str(uuid.uuid4())
        payload = {
            "id": msg_id,
            "session_id": session_id,
            "role": "assistant",
            "content": content,
            "reply_to": reply_to,
            "intent_key": intent_key,
            "metadata": metadata or {}
        }
        try:
            res = await SupabaseService.table_insert("chat_messages", payload)
            if res and getattr(res, "data", None) and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            print(f"[AVISO CHAT_SERVICE] Falha ao persistir resposta da IA: {e}")
        return payload

    @staticmethod
    async def get_recent_history(
        session_id: str,
        limit: int = 10,
        exclude_id: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Recupera as últimas mensagens da sessão para alimentar a memória do LLM.
        Por padrão, recupera até 10 mensagens (5 perguntas do usuário e 5 respostas da IA),
        invertendo a lista para manter a ordem cronológica estrita (mais antiga -> mais recente).
        """
        try:
            def _query(table):
                q = table.select("id, role, content, reply_to, created_at").eq("session_id", session_id)
                if exclude_id:
                    q = q.neq("id", exclude_id)
                return q.order("created_at", desc=True).limit(limit)

            res = await SupabaseService.table_select("chat_messages", _query)
            if res and getattr(res, "data", None):
                # Inverte a ordem para cronológica crescente
                chronological = list(reversed(res.data))
                return [
                    {
                        "role": str(item.get("role", "user")),
                        "content": str(item.get("content", ""))
                    }
                    for item in chronological
                    if item.get("content")
                ]
        except Exception as e:
            print(f"[AVISO CHAT_SERVICE] Falha ao recuperar histórico recente: {e}")
        return []

    @staticmethod
    async def get_session_messages(
        session_token_or_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Recupera o histórico completo da sessão para restauração de tela na interface do usuário.
        Busca tanto por session_id direto quanto via resolução por session_token.
        """
        try:
            session_id = session_token_or_id
            # Verifica se é um session_token antes de consultar mensagens
            session_res = await SupabaseService.table_select(
                "chat_sessions",
                lambda q: q.select("id").eq("session_token", session_token_or_id).limit(1)
            )
            if session_res and getattr(session_res, "data", None) and len(session_res.data) > 0:
                session_id = session_res.data[0].get("id", session_token_or_id)

            def _query(table):
                return table.select("id, role, content, reply_to, intent_key, created_at")\
                    .eq("session_id", session_id)\
                    .order("created_at", desc=False)\
                    .limit(limit)

            res = await SupabaseService.table_select("chat_messages", _query)
            if res and getattr(res, "data", None):
                return res.data
        except Exception as e:
            print(f"[AVISO CHAT_SERVICE] Falha ao buscar histórico de mensagens da sessão: {e}")
        return []
