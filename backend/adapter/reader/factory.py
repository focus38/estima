from backend.adapter.reader.reader import Reader
from backend.adapter.reader.registry import ReaderRegistry


class ReaderFactory:
    @staticmethod
    def create(file_type: str, **kwargs) -> Reader:
        reader = ReaderRegistry.get(file_type)
        return reader(**kwargs)

# Глобальная фабрика
reader_factory = ReaderFactory()