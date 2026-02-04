import logging
from typing import List

from openai import AsyncOpenAI

from backend import config


class EmbeddingClient:
    """
    Клиент для создания embedding через API
    """
    def __init__(self, ai_client: AsyncOpenAI):
        self.ai_client = ai_client
        self.logger = logging.getLogger(__name__)

    async def get_embedding(self, text: str) -> List[float]:
        """
        Получение embedding для текста через API
        """
        try:
            response = await self.ai_client.embeddings.create(
                input=text,
                model=config.EMBEDDING_MODEL
            )
            response.raise_for_status()
            return response.data[0].embedding

        except Exception as ex:
            self.logger.error("Error while request embedding for text.", exc_info=ex)
            raise RuntimeError(f"Error while request embedding for text. {ex}")

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Пакетное получение embeddings
        """
        embeddings = []
        try:
            response = await self.ai_client.embeddings.create(
                input=texts,
                model=config.EMBEDDING_MODEL
            )
            if not response.data:
                raise RuntimeError("Response data is empty.")
            for item in response.data:
                embeddings.append(item.embedding)
            return embeddings

        except Exception as ex:
            self.logger.error("Error while request embedding for batch of text.", exc_info=ex)
            raise RuntimeError(f"Error while request embedding for batch of text. {ex}")