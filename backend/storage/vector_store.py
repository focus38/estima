import asyncio
import uuid
from typing import Dict, List, Any

import chromadb
from chromadb.utils import embedding_functions

from backend import config


class ChromaStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(config.CHROMA_PERSIST_DIR))
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_base=config.AI_PROXY_URL,
            api_key=config.AI_API_KEY,
            model_name=config.EMBEDDING_MODEL
        )
        self.collection = self.client.get_or_create_collection(
            name="estima_knowledge",
            embedding_function=self.embedding_fn
        )

    @staticmethod
    def create_document(row: Dict) -> str:
        """Формирование документа из строки датасета"""
        return (
            f"Задача: {row['task_name']}\n"
            f"Роль: {row['role']}\n"
            f"Трудозатраты: {row['estimate']} часов\n"
            f"Best practice: {row['best_practice']}"
        )

    def add(self, dataset: List[Dict[str, Any]], batch_size: int = 10) -> int:
        """
        Добавление данных из DataFrame в векторное хранилище
        """

        documents = []
        metadatas = []
        ids = []

        # Формирование документов и метаданных
        for row in dataset:
            doc = self.create_document(row)
            documents.append(doc)
            metadatas.append({
                "task_name": row["task_name"],
                "role": row["role"],
                "estimate": int(row["estimate"]),
                "best_practice": row["best_practice"]
            })
            ids.append(str(uuid.uuid4()))

        # Добавление в Chroma
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        return len(documents)

    async def query(self, query_text: str, n_results: int = 5):
        # Chroma не async, поэтому оборачиваем в run_in_executor
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._search, query_text, n_results)

    def _search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Семантический поиск по запросу
        Args:
            query: текстовый запрос
            n_results: количество результатов
        Returns:
            Список результатов с метриками
        """

        # Выполнение поиска
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        # Форматирование результатов
        formatted_results = []
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i] # чем меньше, тем релевантнее
            if distance > config.SIMILARITY_THRESHOLD:
                # Пропускаем результат, как нерелевантный.
                continue
            formatted_results.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": distance
            })

        return formatted_results



chroma_store = ChromaStore()