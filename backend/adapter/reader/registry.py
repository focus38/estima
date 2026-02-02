from typing import Dict, Type

from backend.adapter.reader.reader import Reader


class ReaderRegistry:
    _readers: Dict[str, Type[Reader]] = {}

    @classmethod
    def register(cls, reader_cls: Type[Reader]) -> None:
        file_type = reader_cls.file_type

        if not file_type:
            raise ValueError(f"{reader_cls.__name__} has empty file_type")

        if file_type in cls._readers:
            raise ValueError(f"Reader '{file_type}' already registered")

        cls._readers[file_type] = reader_cls

    @classmethod
    def get(cls, file_type: str) -> Type[Reader]:
        try:
            return cls._readers[file_type]
        except KeyError:
            raise ValueError(f"Unknown reader '{file_type}'.")

def register_reader(cls: Type[Reader]) -> Type[Reader]:
    """
    Декоратор для автоматической регистрации reader.
    :param cls: Класс reader для регистрации.
    :return:
    """
    ReaderRegistry.register(cls)
    return cls