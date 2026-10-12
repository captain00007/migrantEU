from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app.core.config import settings
from app.ai.loader.web_loader import WebLoader
from app.ai.loader.pdf_loader import PDFLoader
from app.ai.cleaners.text_cleaner import TextCleaner

class LiveReaderInput(BaseModel):
    url: str = Field(description="URL oficial do edital ou da página a ser lida.")
    question: str = Field(description="Dúvida específica a ser respondida com base no conteúdo (ex: 'quais documentos necessários?').")

@tool(args_schema=LiveReaderInput)
async def live_url_reader_tool(url: str, question: str) -> str:
    """
    Lê uma página web ou arquivo PDF oficial em tempo real na memória (sem salvar no disco)
    para responder a perguntas detalhadas (como listas de documentos ou cronogramas).
    """
    try:
        if url.lower().endswith(".pdf") or ".pdf?" in url.lower():
            text = await PDFLoader.extract_text_from_url(url)
        else:
            html = await WebLoader.fetch_html(url)
            text = TextCleaner.clean_html(html)

        cleaned = TextCleaner.clean_text(text)
        max_chars = settings.AI_READER_MAX_CHARS
        preview = cleaned[:max_chars] if len(cleaned) > max_chars else cleaned
        header = f"Trecho extraído do edital ({url}) para responder sobre '{question}':"
        return f"{header}\n\n{preview}"
    except Exception as e:
        return f"Não foi possível acessar diretamente o link do edital: {str(e)}. Por favor, oriente o usuário a acessar o link oficial diretamente."
