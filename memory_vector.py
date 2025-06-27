import faiss
import numpy as np
import os
import json
from openai import OpenAI

# === Setup OpenAI client ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

embedding_model = "text-embedding-3-small"
embedding_dim = 1536  # Make sure this matches the model used
INDEX_PATH = "index.faiss"
DATA_PATH = "memory_data.json"

# === Load or create FAISS index ===
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
else:
    index = faiss.IndexFlatL2(embedding_dim)

# === Load stored text memory ===
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r") as f:
        memory_data = json.load(f)
else:
    memory_data = []

# === Generate embedding using latest SDK ===
def embed(text: str) -> np.ndarray:
    response = client.embeddings.create(
        model=embedding_model,
        input=[text]
    )
    return np.array(response.data[0].embedding, dtype=np.float32).reshape(1, -1)

# === Store new memory (text + vector) ===
def store_memory(text: str):
    vec = embed(text)
    index.add(vec)
    memory_data.append(text)

    faiss.write_index(index, INDEX_PATH)
    with open(DATA_PATH, "w") as f:
        json.dump(memory_data, f)

# === Retrieve most relevant memories ===
def retrieve_relevant(query: str, top_k: int = 3):
    if index.ntotal == 0:
        return []
    vec = embed(query)
    D, I = index.search(vec, top_k)
    return [memory_data[i] for i in I[0] if i < len(memory_data)]
