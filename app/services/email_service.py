import asyncio
from typing import List, Dict, Any
import resend
from app.core.config import settings

class EmailService:
    """
    Serviço de envio de e-mails transacionais e em lote utilizando a API do Resend.
    """
    @classmethod
    def _init_resend(cls):
        if settings.RESEND_API_KEY:
            resend.api_key = settings.RESEND_API_KEY

    @classmethod
    async def send_welcome_email(cls, email: str, magic_token: str) -> bool:
        cls._init_resend()
        if not settings.RESEND_API_KEY:
            print(f"[EMAIL SIMULAÇÃO] Boas-vindas para {email} com token {magic_token}")
            return True

        confirmation_url = f"{settings.BASE_URL}/subscribers/confirm/{magic_token}"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #1e3a8a;">Bem-vindo(a) ao migrantEU!</h2>
            <p>Você se cadastrou para receber alertas oficiais sobre editais universitários (Cátedra Sérgio Vieira de Mello), cursos gratuitos de português (PLAC) e apoio humanitário no Brasil.</p>
            <p style="margin: 30px 0;">
                <a href="{confirmation_url}" style="background-color: #2563eb; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    Confirmar Minha Inscrição
                </a>
            </p>
            <p style="font-size: 12px; color: #6b7280;">Se você não realizou esta inscrição, basta ignorar esta mensagem.</p>
        </div>
        """

        def _send():
            params = {
                "from": settings.RESEND_FROM_EMAIL or "notificacoes@migranteu.org",
                "to": [email],
                "subject": "Confirmação de Inscrição — migrantEU Alertas Oficiais",
                "html": html_content
            }
            return resend.Emails.send(params)

        try:
            await asyncio.to_thread(_send)
            return True
        except Exception as e:
            print(f"Erro ao enviar e-mail via Resend: {str(e)}")
            return False

    @classmethod
    async def dispatch_notice_alert_batch(cls, notice: Dict[str, Any], subscribers: List[Dict[str, Any]]) -> int:
        cls._init_resend()
        if not subscribers:
            return 0

        institution_name = notice.get("institution_name") or notice.get("institution_sigla") or "Instituição Oficial"
        title = notice.get("title", "Nova Oportunidade")
        summary = notice.get("summary", "")
        end_date = notice.get("end_date", "")
        notice_url = notice.get("notice_url", "")

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <div style="background-color: #eff6ff; padding: 10px 16px; border-radius: 6px; margin-bottom: 16px;">
                <strong style="color: #1e40af;">NOVO EDITAL OFICIAL APROVADO: {institution_name}</strong>
            </div>
            <h3 style="color: #111827;">{title}</h3>
            <p style="color: #374151; line-height: 1.6;">{summary}</p>
            <p><strong>Prazo limite de inscrição:</strong> {end_date}</p>
            <p style="margin: 25px 0;">
                <a href="{notice_url}" target="_blank" style="background-color: #059669; color: #ffffff; padding: 12px 22px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    Acessar Edital Oficial
                </a>
            </p>
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
            <p style="font-size: 12px; color: #6b7280;">Você recebeu esta mensagem porque é assinante dos alertas da plataforma migrantEU.</p>
        </div>
        """

        sent_count = 0
        for sub in subscribers:
            email = sub.get("email")
            if not email:
                continue

            if not settings.RESEND_API_KEY:
                print(f"[SIMULAÇÃO BATCH EMAIL] Para: {email} | Edital: {title}")
                sent_count += 1
                continue

            def _send_one():
                params = {
                    "from": settings.RESEND_FROM_EMAIL or "notificacoes@migranteu.org",
                    "to": [email],
                    "subject": f"Novo Edital: {institution_name} — {title}",
                    "html": html_content
                }
                return resend.Emails.send(params)

            try:
                await asyncio.to_thread(_send_one)
                sent_count += 1
            except Exception as e:
                print(f"Erro ao enviar para {email}: {e}")

        return sent_count
