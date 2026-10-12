from app.ai.intent import IntentClassifier
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.notice_service import NoticeService
from app.services.community_service import CommunityService
from app.core.database import SupabaseService
from app.core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    notices = await NoticeService.list_active_notices(limit=settings.HOME_NOTICES_LIMIT)
    categories = await NoticeService.list_categories()
    return templates.TemplateResponse(
        request=request,
        name="pages/index.html",
        context={
            "notices": notices,
            "categories": categories
        }
    )

@router.get("/editais", response_class=HTMLResponse)
async def notices_page(
    request: Request,
    categoria: str | None = Query(None),
    uf: str | None = Query(None)
):
    notices = await NoticeService.list_active_notices(category=categoria, uf=uf, limit=settings.CATALOG_NOTICES_LIMIT)
    categories = await NoticeService.list_categories()
    return templates.TemplateResponse(
        request=request,
        name="pages/notices.html",
        context={
            "notices": notices,
            "categories": categories,
            "active_category": categoria,
            "active_uf": uf
        }
    )

@router.get("/comunidades", response_class=HTMLResponse)
async def communities_page(
    request: Request,
    nacionalidade: str | None = Query(None),
    uf: str | None = Query(None)
):
    communities = await CommunityService.list_communities(nationality=nacionalidade, uf=uf, limit=50)
    nationalities = await CommunityService.list_distinct_nationalities()
    return templates.TemplateResponse(
        request=request,
        name="pages/communities.html",
        context={
            "communities": communities,
            "nationalities": nationalities,
            "active_nationality": nacionalidade,
            "active_uf": uf
        }
    )

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, q: str | None = Query(None)):
    initial_intent = await IntentClassifier.detect_intent(q) if q else None
    return templates.TemplateResponse(
        request=request,
        name="pages/chat.html",
        context={"initial_query": q, "initial_intent": initial_intent}
    )

@router.get("/termos-de-uso", response_class=HTMLResponse)
async def terms_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pages/terms.html",
        context={}
    )

@router.get("/privacidade", response_class=HTMLResponse)
async def privacy_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pages/privacy.html",
        context={}
    )

@router.get("/subscribers/confirm/{magic_token}", response_class=HTMLResponse)
async def confirm_subscription(request: Request, magic_token: str):
    await SupabaseService.table_update("subscribers", "magic_token", magic_token, {"is_active": True})
    return HTMLResponse("""
    <html>
      <body style="font-family: sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; background:#f3f7fc;">
        <div style="background:white; padding:40px; border-radius:24px; box-shadow:0 10px 25px -5px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; text-align:center; max-width:480px;">
          <div style="width:48px; height:48px; border-radius:50%; background:#e0f2fe; color:#0284c7; display:flex; align-items:center; justify-content:center; margin:0 auto 16px; font-size:24px; font-weight:bold;">✓</div>
          <h2 style="color:#0f172a; margin-bottom:12px; font-size:22px;">Inscrição Confirmada com Sucesso!</h2>
          <p style="color:#475569; font-size:14px; line-height:1.6;">Você receberá notificações automáticas por e-mail sempre que novos editais de seu interesse forem publicados e aprovados no migrantEU.</p>
          <a href="/" style="display:inline-block; margin-top:24px; padding:12px 24px; background:#0284c7; color:white; text-decoration:none; border-radius:12px; font-weight:bold; font-size:14px;">Voltar à Página Inicial</a>
        </div>
      </body>
    </html>
    """)

@router.get("/unsubscribe/{token}", response_class=HTMLResponse)
@router.get("/subscribers/unsubscribe/{token}", response_class=HTMLResponse)
async def unsubscribe_page(request: Request, token: str):
    try:
        await SupabaseService.table_update("subscribers", "magic_token", token, {"is_active": False})
    except Exception as e:
        print(f"[AVISO] Falha ao desativar subscriber {token}: {e}")
    return templates.TemplateResponse(
        request=request,
        name="pages/unsubscribe.html",
        context={"token": token}
    )
