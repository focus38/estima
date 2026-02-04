import asyncio
from pathlib import Path
from typing import List
from backend import config
from backend.storage.vector_store import ChromaStore


config.CHROMA_PERSIST_DIR = Path("./chroma")

store = ChromaStore()

queries: List[str] = ["Оптимизация SQL-запросов","Разработка стратегии резервирования", "Написание инструкций"]

res = asyncio.run(store.query_batch(queries))

print(res)