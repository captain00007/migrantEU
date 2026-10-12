import markdown
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.core.database import SupabaseService
from app.services.email_service import EmailService
from app.ai.agent import process_chat_message, process_chat_message_with_intent
from app.ai.intent import IntentClassifier, INTENTS_MAP
from app.core.config import settings
from datetime import datetime, timezone
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

    # 2. Processa com o Agente LangChain com prompt especializado pela intenção detectada por LLM
    try:
        result = await process_chat_message(
            user_input=message,
            provider=ai_config.get("llm_provider"),
            model=ai_config.get("llm_model"),
            return_intent=True
        )
        if isinstance(result, tuple) and len(result) == 2:
            ai_reply, detected_intent = result
        else:
            ai_reply = str(result)
            detected_intent = INTENTS_MAP["geral_acolhimento"]
    except Exception as e:
        print(f"[ERRO CHAT ENDPOINT]: {e}")
        ai_reply = "Desculpe, ocorreu uma instabilidade momentânea na conexão com o assistente inteligente. Por favor, tente enviar sua pergunta novamente em instantes."
        detected_intent = INTENTS_MAP["geral_acolhimento"]

    # 3. Retorna os blocos HTML das mensagens para inserção HTMX
    user_bubble = templates.get_template("partials/chat_message.html").render({
        "role": "user",
        "content": message
    })
    ai_formatted = markdown.markdown(ai_reply, extensions=['extra', 'nl2br'])
    ai_bubble = templates.get_template("partials/chat_message.html").render({
        "role": "assistant",
        "content": ai_formatted,
        "intent": detected_intent
    })

    return HTMLResponse(content=user_bubble + "\n" + ai_bubble)

@router.post("/chat/detect-intent")
async def detect_intent_endpoint(request: Request):
    """Endpoint ágil para identificação de intenção em tempo real utilizando LLM."""
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        intent = await IntentClassifier.detect_intent(prompt)
        return JSONResponse(content=intent)
    except Exception as e:
        print(f"[ERRO DETECT INTENT ENDPOINT]: {e}")
        return JSONResponse(content=INTENTS_MAP["geral_acolhimento"])

@router.post("/subscribers", response_class=HTMLResponse)
async def subscribe_endpoint(
    request: Request,
    email: str = Form(...),
    topics: list[str] = Form(default=[]),
    uf_preference: str | None = Form(None),
    terms_consent: bool = Form(default=True)
):
    if not terms_consent:
        return HTMLResponse("""
        <div class="bg-amber-950/60 border border-amber-500/40 text-amber-200 p-6 rounded-3xl text-center space-y-2">
          <p class="text-sm font-bold text-white">Consentimento Obrigatório (LGPD)</p>
          <p class="text-xs">Para cadastrar alertas, é necessário concordar com os Termos de Uso e com a Política de Privacidade.</p>
        </div>
        """)

    try:
        token = str(uuid.uuid4())
        data = {
            "email": email,
            "topics": topics,
            "uf_preference": uf_preference,
            "magic_token": token,
            "is_active": True,
            "consent_at": datetime.now(timezone.utc).isoformat()
        }
        await SupabaseService.table_insert("subscribers", data)
        await EmailService.send_welcome_email(email, token)

        return HTMLResponse("""
        <div class="bg-emerald-950/60 border border-emerald-500/40 text-emerald-100 p-8 rounded-3xl text-center space-y-3 shadow-xl">
          <div class="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-300 flex items-center justify-center mx-auto text-xl font-bold">✓</div>
          <h3 class="text-xl font-black text-white">Inscrição Realizada com Sucesso!</h3>
          <p class="text-xs text-emerald-200 leading-relaxed">
            Seu e-mail foi cadastrado com segurança. Em conformidade com a LGPD, você poderá cancelar sua inscrição a qualquer momento com apenas 1 clique através dos links no rodapé de nossas mensagens.
          </p>
        </div>
        """)
    except Exception as e:
        return HTMLResponse("""
        <div class="bg-rose-950/60 border border-rose-500/40 text-rose-100 p-6 rounded-3xl text-center space-y-1">
          <p class="text-sm font-bold text-white">Aviso</p>
          <p class="text-xs text-rose-200">Este e-mail já está cadastrado ou ocorreu uma instabilidade momentânea. Tente novamente.</p>
        </div>
        """)
