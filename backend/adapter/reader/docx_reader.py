from docx import Document

from backend.adapter.reader.reader import Reader
from backend.adapter.reader.registry import register_reader


@register_reader
class DOCXReader(Reader):
    file_type = "docx"

    def read(self, file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
