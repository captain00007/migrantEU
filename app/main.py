from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.services.scheduler import start_scheduler, stop_scheduler
from app.routers import web, api, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o APScheduler em segundo plano
    start_scheduler()
    print(f"[migrantEU] Servidor iniciado com sucesso em modo: {settings.APP_ENV}")
    yield
    # Encerra o agendador de forma limpa
    stop_scheduler()
    print("[migrantEU] Servidor encerrado.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Central de editais e oportunidades para refugiados e migrantes no Brasil.",
    version="1.0.0",
    lifespan=lifespan
)

# Arquivos estáticos (CSS, JS, PWA Manifest, Ícones)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Inclusão dos roteadores
app.include_router(web.router)
app.include_router(api.router)
app.include_router(admin.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
