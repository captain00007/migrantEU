import re
from bs4 import BeautifulSoup

class TextCleaner:
    """
    Limpa e normaliza textos extraídos de páginas web e documentos de editais.
    """
    @classmethod
    def clean_html(cls, html_content: str) -> str:
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
        return cls.clean_text(text)

    @classmethod
    def clean_text(cls, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        return text.strip()
