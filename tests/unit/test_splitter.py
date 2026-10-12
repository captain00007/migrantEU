import pytest
from app.ai.splitter.text_splitter import NoticeTextSplitter

@pytest.mark.unit
class TestNoticeTextSplitter:
    def test_split_long_text(self):
        splitter = NoticeTextSplitter(chunk_size=100, chunk_overlap=20)
        long_text = "Esta é uma oportunidade da Cátedra Sérgio Vieira de Mello na UFPR para migrantes e refugiados. " * 10
        chunks = splitter.split(long_text)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 150
