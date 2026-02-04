from backend.adapter.reader.reader import Reader
from backend.adapter.reader.registry import register_reader


@register_reader
class MDReader(Reader):
    file_type = "md"

    def read(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
