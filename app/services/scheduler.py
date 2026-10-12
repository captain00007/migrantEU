from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.notice_service import NoticeService
from app.core.config import settings

scheduler = AsyncIOScheduler()

async def scheduled_notice_expiration_job():
    """
    Executa a verificação periódica para marcar editais vencidos como 'expirado'.
    """
    try:
        expired_count = await NoticeService.expire_outdated_notices()
        if expired_count > 0:
            print(f"[SCHEDULER] {expired_count} edital(is) vencido(s) marcado(s) como 'expirado'.")
    except Exception as e:
        print(f"[SCHEDULER ERRO] Falha na rotina de expiração: {e}")

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            scheduled_notice_expiration_job,
            trigger=CronTrigger(hour=settings.SCHEDULER_CRON_HOUR, minute=settings.SCHEDULER_CRON_MINUTE),
            id="expire_outdated_notices",
            name="Expiração diária de editais vencidos",
            replace_existing=True
        )
        scheduler.start()
        print(f"[SCHEDULER] APScheduler iniciado com sucesso (Horário configurado: {settings.SCHEDULER_CRON_HOUR:02d}:{settings.SCHEDULER_CRON_MINUTE:02d}).")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("[SCHEDULER] APScheduler encerrado.")
