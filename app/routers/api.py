from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.database import SupabaseService
from app.services.email_service import EmailService
from app.ai.agent import process_chat_message
from app.core.config import settings
import uuid

router = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="app/templates")

@router.post("/chat/message", response_class=HTMLResponse)
async def chat_message_endpoint(
    request: Request,
    message: str = Form(...)
):
    # 1. Carrega switch ativo de IA de system_settings (ou fallback de settings)
    ai_config = {"llm_provider": settings.AI_LLM_PROVIDER, "llm_model": settings.AI_LLM_MODEL}
    try:
        setting_res = await SupabaseService.table_select("system_settings", lambda q: q.select("*").eq("key", "ai_config").limit(1))
        if setting_res.data:
            ai_config = setting_res.data[0].get("value", ai_config)
    except Exception as e:
        print(f"[AVISO] Usando config de IA local: {e}")

    # 2. Processa com o Agente LangChain
    ai_reply = await process_chat_message(
        user_input=message,
        provider=ai_config.get("llm_provider"),
        model=ai_config.get("llm_model")
    )

    # 3. Retorna os blocos HTML das mensagens para inserção HTMX
    user_bubble = templates.get_template("partials/chat_message.html").render({
        "role": "user",
        "content": message
    })
    ai_bubble = templates.get_template("partials/chat_message.html").render({
        "role": "assistant",
        "content": ai_reply
    })

    return HTMLResponse(content=user_bubble + "\n" + ai_bubble)

@router.post("/subscribers", response_class=HTMLResponse)
async def subscribe_endpoint(
    request: Request,
    email: str = Form(...),
    topics: list[str] = Form(default=[]),
    uf_preference: str | None = Form(None)
):
    try:
        token = str(uuid.uuid4())
        data = {
            "email": email,
            "topics": topics,
            "uf_preference": uf_preference,
            "magic_token": token,
            "is_active": True
        }
        await SupabaseService.table_insert("subscribers", data)
        await EmailService.send_welcome_email(email, token)

        return HTMLResponse("""
        <div class="bg-emerald-900/40 border border-emerald-500/30 text-emerald-100 p-8 rounded-3xl text-center space-y-3">
          <div class="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-300 flex items-center justify-center mx-auto text-xl font-bold">✓</div>
          <h3 class="text-xl font-bold text-white">Inscrição Realizada com Sucesso!</h3>
          <p class="text-xs text-emerald-200">Enviamos um e-mail de confirmação para você. Fique atento(a) à sua caixa de entrada!</p>
        </div>
        """)
    except Exception as e:
        return HTMLResponse("""
        <div class="bg-rose-900/40 border border-rose-500/30 text-rose-100 p-6 rounded-3xl text-center">
          <p class="text-sm font-semibold">Este e-mail já está cadastrado ou ocorreu uma instabilidade. Tente novamente.</p>
        </div>
        """)
