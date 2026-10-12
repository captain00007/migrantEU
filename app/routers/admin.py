from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.database import SupabaseService
from app.core.security import verify_supabase_admin_token
from app.services.notice_service import NoticeService
from app.core.config import settings

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")

async def get_current_admin(request: Request) -> dict:
    token = request.cookies.get(settings.ADMIN_SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/admin/login"})
    user = await verify_supabase_admin_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/admin/login"})
    return user

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str | None = None):
    return templates.TemplateResponse(
        request=request,
        name="pages/login.html",
        context={"error": error}
    )

@router.post("/login")
async def login_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        # Autenticação nativa via Supabase Auth (auth.users)
        auth_response = await SupabaseService.auth_sign_in(email, password)
        if not auth_response or not auth_response.session:
            return templates.TemplateResponse(
                request=request,
                name="pages/login.html",
                context={"error": "E-mail ou senha incorretos."}
            )

        token = auth_response.session.access_token
        response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key=settings.ADMIN_SESSION_COOKIE_NAME,
            value=token,
            httponly=True,
            max_age=settings.ADMIN_SESSION_MAX_AGE_SECONDS,
            samesite="lax"
        )
        return response
    except Exception as e:
        error_msg = "Credenciais inválidas. Verifique seu e-mail e senha no Supabase."
        if "Email not confirmed" in str(e):
            error_msg = "E-mail ainda não confirmado no Supabase Auth."
        return templates.TemplateResponse(
            request=request,
            name="pages/login.html",
            context={"error": error_msg}
        )

@router.get("/logout")
async def logout_action(request: Request):
    token = request.cookies.get(settings.ADMIN_SESSION_COOKIE_NAME)
    if token:
        await SupabaseService.auth_sign_out(token)
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(settings.ADMIN_SESSION_COOKIE_NAME)
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user: dict = Depends(get_current_admin)
):
    pending_notices = await NoticeService.list_pending_notices()
    
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

    return templates.TemplateResponse(
        request=request,
        name="pages/admin.html",
        context={
            "pending_notices": pending_notices,
            "ai_config": ai_config,
            "user": current_user
        }
    )

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
        "embedding_provider": settings.AI_EMBEDDING_PROVIDER,
        "embedding_model": settings.AI_EMBEDDING_MODEL,
        "embedding_dimensions": settings.AI_EMBEDDING_DIMENSIONS
    }
    
    try:
        check = await SupabaseService.table_select("system_settings", lambda q: q.select("*").eq("key", "ai_config"))
        if check.data:
            await SupabaseService.table_update("system_settings", "key", "ai_config", {"value": payload, "updated_by": current_user.get("id")})
        else:
            await SupabaseService.table_insert("system_settings", {"key": "ai_config", "value": payload, "updated_by": current_user.get("id")})
    except Exception as e:
        print(f"Erro ao salvar configurações de IA: {e}")

    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
