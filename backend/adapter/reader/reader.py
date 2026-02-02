from abc import ABC, abstractmethod
from typing import ClassVar


class Reader(ABC):
    """
    Абстракция для reader.
    """

    file_type: ClassVar[str]

    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def read(self, file_path: str) -> str:
        pass
