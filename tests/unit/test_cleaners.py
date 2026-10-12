import pytest
from app.ai.cleaners.text_cleaner import TextCleaner

@pytest.mark.unit
class TestTextCleaner:
    def test_clean_html_removes_scripts_and_styles(self):
        html = """
        <html>
            <head><style>body { color: red; }</style></head>
            <body>
                <script>alert('hack');</script>
                <h1>Edital Sérgio Vieira de Mello</h1>
                <p>Inscrições abertas até 30 de novembro.</p>
                <footer>Rodapé de direitos</footer>
            </body>
        </html>
        """
        cleaned = TextCleaner.clean_html(html)
        assert "alert('hack')" not in cleaned
        assert "color: red" not in cleaned
        assert "Rodapé de direitos" not in cleaned
        assert "Edital Sérgio Vieira de Mello" in cleaned
        assert "Inscrições abertas até 30 de novembro" in cleaned

    def test_clean_text_normalizes_whitespace(self):
        raw = "Texto   com    muitos      espaços\n\n\n\nE quebras extras."
        cleaned = TextCleaner.clean_text(raw)
        assert "Texto com muitos espaços" in cleaned
        assert "\n\n" in cleaned
