import asyncio
from typing import List, Dict, Any
import resend
from app.core.config import settings

class EmailService:
    """
    Serviço de envio de e-mails transacionais e em lote utilizando a API do Resend,
    com suporte a links de descadastramento (opt-out LGPD) e disclaimers legais obrigatórios.
    """
    @classmethod
    def _init_resend(cls):
        if settings.RESEND_API_KEY:
            resend.api_key = settings.RESEND_API_KEY

    @classmethod
    async def send_welcome_email(cls, email: str, magic_token: str) -> bool:
        cls._init_resend()
        confirmation_url = f"{settings.BASE_URL}/subscribers/confirm/{magic_token}"
        unsubscribe_url = f"{settings.BASE_URL}/unsubscribe/{magic_token}"

        if not settings.RESEND_API_KEY:
            print(f"[EMAIL SIMULAÇÃO] Boas-vindas para {email} com token {magic_token} (Opt-out: {unsubscribe_url})")
            return True

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #0284c7; margin: 0;">Bem-vindo(a) ao migrantEU!</h2>
                <p style="color: #64748b; font-size: 13px; margin-top: 4px;">Acolhimento & Oportunidades Acadêmicas</p>
            </div>
            <p style="color: #334155; line-height: 1.6; font-size: 14px;">
                Você se cadastrou para receber alertas oficiais sobre editais universitários, vagas especiais, cursos gratuitos de português (PLAC) e redes de acolhimento no Brasil.
            </p>
            <p style="margin: 30px 0; text-align: center;">
                <a href="{confirmation_url}" style="background-color: #0284c7; color: #ffffff; padding: 12px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 14px; display: inline-block;">
                    Confirmar Minha Inscrição
                </a>
            </p>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
            <p style="font-size: 11px; color: #64748b; line-height: 1.5; margin-bottom: 12px;">
                <strong>Aviso Legal & Isenção:</strong> O migrantEU é um agregador informativo independente, sem vínculo oficial com órgãos governamentais ou universidades. A leitura e conferência definitiva dos requisitos devem ocorrer no edital oficial de cada instituição.
            </p>
            <p style="font-size: 11px; color: #94a3b8; text-align: center; margin: 0;">
                Se deseja deixar de receber nossos comunicados: 
                <a href="{unsubscribe_url}" style="color: #0284c7; text-decoration: underline;">Cancelar inscrição / Deixar de receber alertas</a>
            </p>
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

        sent_count = 0
        for sub in subscribers:
            email = sub.get("email")
            magic_token = sub.get("magic_token", "")
            if not email:
                continue

            unsubscribe_url = f"{settings.BASE_URL}/unsubscribe/{magic_token}"

            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
                <div style="background-color: #f0f9ff; border: 1px solid #bae6fd; padding: 12px 18px; border-radius: 8px; margin-bottom: 20px;">
                    <strong style="color: #0369a1; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">
                        NOVO EDITAL OFICIAL DIVULGADO: {institution_name}
                    </strong>
                </div>
                <h2 style="color: #0f172a; margin-top: 0; font-size: 20px;">{title}</h2>
                <p style="color: #334155; line-height: 1.6; font-size: 14px;">{summary}</p>
                <div style="background: #f8fafc; border-left: 4px solid #0284c7; padding: 10px 14px; margin: 20px 0; font-size: 13px; color: #475569;">
                    <strong>Prazo limite de inscrições:</strong> <span style="color: #e11d48; font-weight: bold;">{end_date}</span>
                </div>
                <p style="margin: 25px 0; text-align: center;">
                    <a href="{notice_url}" target="_blank" style="background-color: #0284c7; color: #ffffff; padding: 12px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 14px; display: inline-block;">
                        Acessar Edital Oficial no Portal da Instituição &rarr;
                    </a>
                </p>
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
                <p style="font-size: 11px; color: #64748b; line-height: 1.5; margin-bottom: 12px;">
                    <strong>Isenção de Responsabilidade (Disclaimer):</strong> O migrantEU é um agregador independente de informações públicas. A inscrição, envio de documentos e conferência de eventuais retificações ou mudanças de cronograma devem ocorrer obrigatoriamente no portal oficial da instituição responsável.
                </p>
                <p style="font-size: 11px; color: #94a3b8; text-align: center; margin: 0;">
                    Você está recebendo este e-mail porque se cadastrou no migrantEU.<br>
                    <a href="{unsubscribe_url}" style="color: #0284c7; text-decoration: underline;">Cancelar inscrição / Deixar de receber alertas</a>
                </p>
            </div>
            """

            if not settings.RESEND_API_KEY:
                print(f"[SIMULAÇÃO BATCH EMAIL] Para: {email} | Edital: {title} | Unsubscribe: {unsubscribe_url}")
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
