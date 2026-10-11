from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.database import SupabaseService
from app.core.security import verify_password, create_access_token, decode_access_token
from app.services.notice_service import NoticeService
from app.core.config import settings

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")

async def get_current_admin(request: Request) -> dict:
    token = request.cookies.get("migranteu_admin_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/admin/login"})
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/admin/login"})
    return payload

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str | None = None):
    return templates.TemplateResponse("pages/login.html", {
        "request": request,
        "error": error
    })

@router.post("/login")
async def login_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    def find_user(q):
        return q.select("*").eq("email", email).eq("is_active", True).limit(1)

    res = await SupabaseService.table_select("users", find_user)
    if not res.data:
        return templates.TemplateResponse("pages/login.html", {
            "request": request,
            "error": "Credenciais inválidas. Verifique seu e-mail e senha."
        })

    user = res.data[0]
    if not verify_password(password, user["hashed_password"]):
        return templates.TemplateResponse("pages/login.html", {
            "request": request,
            "error": "Senha incorreta."
        })

    token = create_access_token({"sub": user["id"], "email": user["email"], "role": user["role"]})
    response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="migranteu_admin_token", value=token, httponly=True, max_age=86400)
    return response

@router.get("/logout")
async def logout_action():
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("migranteu_admin_token")
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user: dict = Depends(get_current_admin)
):
    pending_notices = await NoticeService.list_pending_notices()
    
    # Busca configuração de IA atual
    ai_config = {
        "llm_provider": settings.AI_LLM_PROVIDER,
        "llm_model": settings.AI_LLM_MODEL
    }
    try:
        setting_res = await SupabaseService.table_select("system_settings", lambda q: q.select("*").eq("key", "ai_config").limit(1))
        if setting_res.data:
            ai_config = setting_res.data[0].get("value", ai_config)
    except Exception as e:
        print(f"Erro ao ler system_settings: {e}")

    return templates.TemplateResponse("pages/admin.html", {
        "request": request,
        "pending_notices": pending_notices,
        "ai_config": ai_config,
        "user": current_user
    })

@router.post("/notices/{notice_id}/approve", response_class=HTMLResponse)
async def approve_notice_endpoint(
    notice_id: str,
    current_user: dict = Depends(get_current_admin)
):
    try:
        result = await NoticeService.approve_notice(notice_id)
        emails = result.get("emails_dispatched", 0)
        return HTMLResponse(f"""
        <div class="py-3 px-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold flex items-center justify-between">
          <span>✓ Edital aprovado e publicado com sucesso! ({emails} alertas por e-mail disparados)</span>
        </div>
        """)
    except Exception as e:
        return HTMLResponse(f"""
        <div class="py-3 px-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-bold">
          Erro ao aprovar edital: {str(e)}
        </div>
        """)

@router.post("/notices/{notice_id}/reject", response_class=HTMLResponse)
async def reject_notice_endpoint(
    notice_id: str,
    current_user: dict = Depends(get_current_admin)
):
    await NoticeService.reject_notice(notice_id)
    return HTMLResponse("")

@router.post("/ai-settings")
async def update_ai_settings(
    request: Request,
    llm_provider: str = Form(...),
    llm_model: str = Form(...),
    current_user: dict = Depends(get_current_admin)
):
    payload = {
        "llm_provider": llm_provider,
        "llm_model": llm_model,
        "embedding_provider": "google",
        "embedding_model": "models/text-embedding-004",
        "embedding_dimensions": 768
    }
    
    # Atualiza ou insere na tabela system_settings
    try:
        check = await SupabaseService.table_select("system_settings", lambda q: q.select("*").eq("key", "ai_config"))
        if check.data:
            await SupabaseService.table_update("system_settings", "key", "ai_config", {"value": payload, "updated_by": current_user.get("sub")})
        else:
            await SupabaseService.table_insert("system_settings", {"key": "ai_config", "value": payload, "updated_by": current_user.get("sub")})
    except Exception as e:
        print(f"Erro ao salvar configurações de IA: {e}")

    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
