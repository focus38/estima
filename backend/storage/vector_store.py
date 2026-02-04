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
            metadata={"hnsw:space": "cosine"},
            embedding_function=self.embedding_fn
        )

    @staticmethod
    def create_document(row: Dict) -> str:
        """
        Формирование документа.
        """
        return f"Задача: {row['task_name']}\nРоль: {row['role']}"

    @staticmethod
    def create_metadata(row: Dict) -> Dict[str, Any]:
        """
        Формирование метаданных.
        """
        return {
            "estimate": int(row["estimate"]),
            "best_practice": row["best_practice"]
        }

    def add(self, dataset: List[Dict[str, Any]], batch_size: int = 10) -> int:
        """
        Добавление данных из списка словарей в векторное хранилище с поддержкой батчей.
        Args:
            dataset: список словарей с данными,
            batch_size: размер батча для добавления в хранилище.
        Returns:
            Общее количество добавленных документов.
        """
        total_added = 0

        # Обрабатываем данные по батчам
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i:i + batch_size]

            documents = []
            metadatas = []
            ids = []

            for row in batch:
                doc_id = str(uuid.uuid4())
                doc = self.create_document(row)
                meta = self.create_metadata(row)
                documents.append(doc)
                metadatas.append(meta)
                ids.append(doc_id)

            # Добавление текущего батча в Chroma
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

            total_added += len(documents)

        return total_added

    async def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        # Chroma не async, поэтому оборачиваем в run_in_executor
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self._search, [query_text], n_results)
        return result[0]

    async def query_batch(self, queries: List[str], n_results: int = 5) -> List[List[Dict[str, Any]]]:
        # Chroma не async, поэтому оборачиваем в run_in_executor
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._search, queries, n_results)

    def _search(self, texts: List[str], n_results: int = 5) -> List[List[Dict[str, Any]]]:
        """
        Семантический поиск по запросу
        Args:
            texts: текстовые запросы
            n_results: количество результатов
        Returns:
            Список результатов с метриками
        """

        # Выполнение поиска
        results = self.collection.query(
            query_texts=texts,
            n_results=n_results
        )
        # Форматирование результатов
        formatted_results = []
        for i in range(len(results["ids"])):
            ids = results["ids"][i]
            task_result = []
            for j in range(len(ids)):
                distance = results["distances"][i][j] # Чем меньше, тем релевантнее
                if distance > config.SIMILARITY_THRESHOLD:
                   # Пропускаем результат, как нерелевантный.
                   continue
                task_result.append({
                    "document": results["documents"][i][j],
                    "metadata": results["metadatas"][i][j],
                    "distance": distance
                })
            formatted_results.append(task_result)

        return formatted_results



chroma_store = ChromaStore()