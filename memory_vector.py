import faiss
import numpy as np
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# FAISS index (1536 for ada-002, 1536+ for text-embedding-3-small)
embedding_dim = 1536
index = faiss.IndexFlatL2(embedding_dim)
memory_data = []

def embed(text: str) -> np.ndarray:
    response = openai.Embedding.create(
        model="text-embedding-3-small",
        input=[text]
    )
    return np.array(response["data"][0]["embedding"]).reshape(1, -1)

def store_memory(text: str):
    vec = embed(text)
    index.add(vec)
    memory_data.append(text)


def retrieve_relevant(query: str, top_k: int = 3):
    if index.ntotal == 0:
        return []  # Return empty if no vectors added yet

    vec = embed(query)
    D, I = index.search(vec, top_k)
    return [memory_data[i] for i in I[0] if i < len(memory_data)]
