from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import sqlite3

DB_NAME = "project_knowledge.db"

try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print("Model load error:", e)


def fetch_functions():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, calls FROM functions")
    rows = cursor.fetchall()
    conn.close()
    return rows


def build_vector_store():
    data = fetch_functions()

    texts = [
        f"Function: {row[1]} | Calls: {row[2]}"
        for row in data
    ]

    # Handle empty database case
    if not texts:
        print("⚠️  No functions in database. Creating empty vector store.")
        dimension = 384  # Default dimension for all-MiniLM-L6-v2
        index = faiss.IndexFlatL2(dimension)
        return index, texts

    embeddings = model.encode(texts)
    
    # Handle case where embeddings might be 1D
    if len(embeddings.shape) == 1:
        embeddings = embeddings.reshape(-1, 1)
    
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    return index, texts


def search(query, index, texts, top_k=3):
    if not texts:
        return []
    
    query_embedding = model.encode([query])
    D, I = index.search(np.array(query_embedding), min(top_k, len(texts)))
    results = [texts[i] for i in I[0] if i < len(texts)]
    return results