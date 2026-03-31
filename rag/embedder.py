from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import sqlite3

DB_NAME = "project_knowledge.db"

model = SentenceTransformer("all-MiniLM-L6-v2")


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

    embeddings = model.encode(texts)
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    return index, texts


def search(query, index, texts, top_k=3):
    query_embedding = model.encode([query])
    D, I = index.search(np.array(query_embedding), top_k)
    results = [texts[i] for i in I[0]]
    return results