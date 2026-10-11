from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

class NoticeTextSplitter:
    """
    Divide documentos longos em chunks semânticos para vetorização.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def split(self, text: str) -> List[str]:
        return self.splitter.split_text(text)
