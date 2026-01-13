import os
import pandas as pd
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from tqdm import tqdm

# Путь к CSV-файлу
CSV_PATH = "tasks_dataset.csv"
# Папка для хранения Chroma DB
CHROMA_DB_PATH = "./chroma_db"
# Имя коллекции
COLLECTION_NAME = "tasks"


def main():
    print("Загрузка данных...")
    df = pd.read_csv(CSV_PATH, encoding="utf-8")
    required_columns = ['task_name', 'role', 'estimate', 'best_practice']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"CSV должен содержать колонки: {required_columns}")

    # Объединяем текст для эмбеддингов
    df['text_for_embedding'] = df['task_name'] + " " + df['best_practice']

    # Подготовка метаданных и документов
    documents = df['text_for_embedding'].tolist()
    metadatas = df[['task_name', 'role', 'estimate', 'best_practice']].to_dict(orient='records')
    ids = [f"task_{i}" for i in range(len(documents))]

    print(f"Загружено {len(documents)} задач.")

    # Инициализация Chroma
    print("Инициализация Chroma...")
    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    client = PersistentClient(path=CHROMA_DB_PATH)

    # Удалим коллекцию, если она существует (опционально — для пересоздания)
    # Если вы хотите апдейтить — лучше реализовать upsert логику
    try:
        client.delete_collection(COLLECTION_NAME)
    except:
        pass  # Игнорируем, если коллекции нет

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"}  # опционально
    )

    # Пакетная вставка
    print("Генерация эмбеддингов и загрузка в Chroma...")
    batch_size = 100
    for i in tqdm(range(0, len(documents), batch_size)):
        batch_docs = documents[i:i + batch_size]
        batch_metas = metadatas[i:i + batch_size]
        batch_ids = ids[i:i + batch_size]
        collection.add(
            documents=batch_docs,
            metadatas=batch_metas,
            ids=batch_ids
        )

    print(f"✅ Загружено {collection.count()} задач в коллекцию '{COLLECTION_NAME}' в {CHROMA_DB_PATH}")


if __name__ == "__main__":
    main()