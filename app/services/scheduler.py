from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.notice_service import NoticeService

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
        # Roda todo dia à meia-noite (00:05)
        scheduler.add_job(
            scheduled_notice_expiration_job,
            trigger=CronTrigger(hour=0, minute=5),
            id="expire_outdated_notices",
            name="Expiração diária de editais vencidos",
            replace_existing=True
        )
        scheduler.start()
        print("[SCHEDULER] APScheduler iniciado com sucesso.")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("[SCHEDULER] APScheduler encerrado.")
