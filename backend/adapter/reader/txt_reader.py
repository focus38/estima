from backend.adapter.reader.reader import Reader
from backend.adapter.reader.registry import register_reader

@register_reader
class TXTReader(Reader):
    file_type = "txt"

    def read(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
