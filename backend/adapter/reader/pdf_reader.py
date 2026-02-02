from PyPDF2 import PdfReader

from backend.adapter.reader.reader import Reader
from backend.adapter.reader.registry import register_reader


@register_reader
class PDFReader(Reader):
    file_type = "pdf"

    def read(self, file_path: str) -> str:
        try:
            pdf = PdfReader(file_path)
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            raise RuntimeError(f"Ошибка при чтении PDF-файла {file_path}: {e}")