from typing import Optional, Dict, Any
from app.core.database import SupabaseService

async def verify_supabase_admin_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Valida o token JWT de sessão junto ao Supabase Auth e extrai dados
    de identificação e papel (role) do operador.
    """
    if not token:
        return None
    try:
        res = await SupabaseService.auth_get_user(token)
        if not res or not res.user:
            return None

        user = res.user
        metadata = user.user_metadata or {}
        role = metadata.get("role", "admin")  # Padrão admin caso não especificado no cadastro

        return {
            "id": user.id,
            "email": user.email,
            "role": role,
            "full_name": metadata.get("full_name", user.email.split("@")[0])
        }
    except Exception:
        return None
