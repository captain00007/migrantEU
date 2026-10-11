from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.notice_service import NoticeService
from app.core.database import SupabaseService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    notices = await NoticeService.list_active_notices(limit=6)
    return templates.TemplateResponse("pages/index.html", {
        "request": request,
        "notices": notices
    })

@router.get("/editais", response_class=HTMLResponse)
async def notices_page(
    request: Request,
    categoria: str | None = Query(None),
    uf: str | None = Query(None)
):
    notices = await NoticeService.list_active_notices(category=categoria, uf=uf, limit=50)
    return templates.TemplateResponse("pages/notices.html", {
        "request": request,
        "notices": notices,
        "active_category": categoria,
        "active_uf": uf
    })

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("pages/chat.html", {
        "request": request
    })

@router.get("/subscribers/confirm/{magic_token}", response_class=HTMLResponse)
async def confirm_subscription(request: Request, magic_token: str):
    await SupabaseService.table_update("subscribers", "magic_token", magic_token, {"is_active": True})
    return HTMLResponse("""
    <html>
      <body style="font-family: sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; background:#f8fafc;">
        <div style="background:white; padding:40px; border-radius:16px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1); text-align:center; max-width:480px;">
          <h2 style="color:#2563eb; margin-bottom:12px;">Inscrição Confirmada com Sucesso! 🎉</h2>
          <p style="color:#475569; font-size:14px; line-height:1.6;">Você receberá notificações automáticas por e-mail sempre que novos editais de seu interesse forem publicados e aprovados no migrantEU.</p>
          <a href="/" style="display:inline-block; margin-top:24px; padding:10px 20px; background:#2563eb; color:white; text-decoration:none; border-radius:8px; font-weight:bold; font-size:14px;">Voltar à Página Inicial</a>
        </div>
      </body>
    </html>
    """)
