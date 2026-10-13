import markdown
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.core.database import SupabaseService
from app.services.email_service import EmailService
from app.services.chat_service import ChatService
from app.ai.agent import process_chat_message, process_chat_message_with_intent
from app.ai.intent import IntentClassifier, INTENTS_MAP
from app.ai.guardrails.safety_guard import SafetyGuard
from app.core.config import settings
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="app/templates")

@router.post("/chat/message", response_class=HTMLResponse)
async def chat_message_endpoint(
    request: Request,
    message: str = Form(...),
    session_id: str | None = Form(None)
):
    # 1. Identificação ou criação da sessão do cliente sem fricção de login
    session_token = session_id or request.cookies.get("chat_session_id")
    if not session_token:
        session_token = str(uuid.uuid4())

    session = await ChatService.get_or_create_session(
        session_token=session_token,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    actual_session_id = session.get("id") or session_token

    # 2. Validação estrita de regras de segurança e proteção do assistente
    is_safe, violation_reason = SafetyGuard.check_safety(message)
    if not is_safe:
        # Se a pergunta violar regra de segurança, NUNCA é armazenada no histórico!
        ai_reply = (
            "Sua mensagem não pôde ser processada porque contém termos ou instruções "
            "que violam as diretrizes de segurança da plataforma **migrantEU**. "
            "Por favor, reformule sua dúvida sobre editais universitários, cursos de português (PLAC), "
            "regularização documental ou acolhimento a migrantes e refugiados."
        )
        user_bubble = templates.get_template("partials/chat_message.html").render({
            "role": "user",
            "content": SafetyGuard.sanitize_input(message)
        })
        ai_bubble = templates.get_template("partials/chat_message.html").render({
            "role": "assistant",
            "content": ai_reply,
            "is_security_alert": True
        })
        response = HTMLResponse(content=user_bubble + "\n" + ai_bubble)
        response.set_cookie(
            "chat_session_id",
            session_token,
            httponly=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 30
        )
        return response

    # 3. Pergunta segura: persiste a mensagem do usuário no histórico
    user_msg = await ChatService.save_user_message(
        session_id=actual_session_id,
        content=message
    )
    user_msg_id = user_msg.get("id")

    # 4. Recupera histórico recente da sessão (limite de 10 mensagens = 5 perguntas + 5 respostas anteriores)
    recent_history = await ChatService.get_recent_history(
        session_id=actual_session_id,
        limit=10,
        exclude_id=user_msg_id
    )

    # 5. Carrega switch ativo de IA de system_settings (ou fallback de settings)
    ai_config = {"llm_provider": settings.AI_LLM_PROVIDER, "llm_model": settings.AI_LLM_MODEL}
    try:
        setting_res = await SupabaseService.table_select("system_settings", lambda q: q.select("*").eq("key", "ai_config").limit(1))
        if setting_res.data:
            ai_config = setting_res.data[0].get("value", ai_config)
    except Exception as e:
        print(f"[AVISO] Usando config de IA local: {e}")

    # 6. Processa com o Agente LangChain alimentado com o histórico recente
    try:
        result = await process_chat_message(
            user_input=message,
            chat_history=recent_history,
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

    # 7. Persiste a resposta da IA vinculada à pergunta via reply_to
    await ChatService.save_ai_message(
        session_id=actual_session_id,
        content=ai_reply,
        reply_to=user_msg_id,
        intent_key=detected_intent.get("key") if isinstance(detected_intent, dict) else None
    )

    # 8. Retorna os blocos HTML das mensagens para inserção reativa HTMX
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

    response = HTMLResponse(content=user_bubble + "\n" + ai_bubble)
    response.set_cookie(
        "chat_session_id",
        session_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30
    )
    return response

@router.post("/chat/reset", response_class=HTMLResponse)
async def chat_reset_endpoint(request: Request):
    """Reinicia a sessão de conversação do usuário de forma transparente."""
    new_token = str(uuid.uuid4())
    await ChatService.get_or_create_session(new_token)

    initial_bubble = """
    <div class="flex gap-3 mb-4 chat-bubble-enter">
      <div class="w-8 h-8 rounded-xl bg-gradient-to-tr from-sky-500 to-blue-600 flex-shrink-0 flex items-center justify-center text-white text-xs font-black shadow-md shadow-sky-500/20">
        IA
      </div>
      <div class="bg-slate-50 border border-slate-200/80 text-slate-800 rounded-2xl rounded-bl-none p-5 text-sm leading-relaxed max-w-[85%] shadow-sm">
        <p class="font-extrabold text-slate-900 mb-1.5 text-base">Conversa reiniciada com sucesso! 👋</p>
        <p class="text-slate-600">Como podemos ajudar você hoje? Diga o que procura ou escolha uma sugestão abaixo. Nosso assistente localiza editais, cursos e orientações oficiais no Brasil.</p>
      </div>
    </div>
    """
    response = HTMLResponse(content=initial_bubble)
    response.set_cookie(
        "chat_session_id",
        new_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30
    )
    return response

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
