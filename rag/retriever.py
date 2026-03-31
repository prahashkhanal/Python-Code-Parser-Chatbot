import requests
from rag.embedder import build_vector_store, search


OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_llama(prompt):

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)

    return response.json()["response"]


if __name__ == "__main__":

    print("Starting RAG system...")

    try:
        index, texts = build_vector_store()

        print("Vector store built.")
        print("Indexed texts:", texts)
        print("Number of indexed texts:", len(texts))

    except Exception as e:
        print("Error building vector store:", e)
        exit()

    if len(texts) == 0:
        print("No data found in database. Exiting.")
        exit()

    print("\nRAG Ready!\n")

    while True:

        query = input("Ask about project: ")

        if query.lower() in ["exit", "quit"]:
            break

        context = search(query, index, texts)

        full_prompt = f"""
You are an AI assistant that explains Python projects.

Use the provided project context to answer questions.

Project Context:
{context}

User Question:
{query}

Give a clear technical explanation.
"""

        answer = ask_llama(full_prompt)

        print("\nAI Answer:\n")
        print(answer)