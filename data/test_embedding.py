import asyncio
from pathlib import Path
from typing import Dict, Any, List

from backend import config
from backend.storage.vector_store import ChromaStore


config.CHROMA_PERSIST_DIR = Path("./chroma")

def create_document(row: Dict[str, Any]) -> str:
    """Формирование документа из строки датасета"""
    return (
        f"Задача: {row['task_name']}\n"
        f"Роль: {row['role']}\n"
        f"Трудозатраты: {row['estimate']} часов\n"
        f"Best practice: {row['best_practice']}"
    )

store = ChromaStore()

dataset: List[Dict[str, Any]] = [
    {
        "task_name": "Оптимизация SQL-запросов в модуле отчетов",
        "role": "backend",
        "estimate": 12,
        "best_practice": "Применять EXPLAIN ANALYZE и индексацию по частым условиям фильтрации"
    },
    {
        "task_name": "Разработка стратегии disaster recovery и резервирования",
        "role": "architect",
        "estimate": 32,
        "best_practice": "Обеспечить RTO/RPO в соответствии с бизнес-требованиями"
    }
]

num_of_rows = store.add(dataset)
print(f"Added {num_of_rows}")

text = create_document(dataset[1])

res = asyncio.run(store.query(text))

print(res)