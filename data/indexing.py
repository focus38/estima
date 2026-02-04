import pandas as pd

from backend.storage.vector_store import ChromaStore


df = pd.read_csv("tasks_dataset.csv")

store = ChromaStore()
dataset = df.to_dict(orient="records")
num_documents = store.add(dataset)
print(f"Number of documents added to vector storage: {num_documents}")