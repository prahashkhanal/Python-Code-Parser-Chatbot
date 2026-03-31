from flask import Flask, request, jsonify, render_template
from rag.embedder import build_vector_store, search
from parser.ast_parser import analyze_directory
from parser.graph_builder import build_call_graph
from storage.database import create_tables, insert_file, insert_function
import requests
import os
import git
import sqlite3

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
PROJECT_FOLDER = "analyzed_repo"

print("Building vector store...")
index, texts = build_vector_store()
print("Vector store ready.")


def ask_llama(prompt):
    payload = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    data = response.json()

    if "response" not in data:
        print("Ollama error:", data)
        return "AI could not generate response."

    return data["response"]


# 🔥 MAIN FEATURE
def generate_project_insight():

    conn = sqlite3.connect("project_knowledge.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, calls FROM functions")
    data = cursor.fetchall()

    conn.close()

    if not data:
        return "No data available."

    functions = [row[0] for row in data][:10]

    flow_lines = []
    for name, calls in data[:15]:
        try:
            calls_list = eval(calls)
            for c in calls_list:
                flow_lines.append(f"{name} → {c}")
        except:
            continue

    flow_text = "\n".join(flow_lines[:10])

    prompt = f"""
You are explaining a Python project to a new developer.

Functions:
{functions}

Flow:
{flow_text}

Give output in this format:

1. Project Summary (2-3 lines)
2. Key Functions (with simple explanation)
3. Flow (arrow format)
4. Flow Explanation (step-by-step in simple English)

Keep it clear and beginner-friendly.
"""

    return ask_llama(prompt)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/project_insight")
def project_insight():
    result = generate_project_insight()
    return jsonify({"result": result})


@app.route("/ask", methods=["POST"])
def ask():

    question = request.json["question"]
    context = search(question, index, texts)[:3]

    prompt = f"""
You are a software engineer.

Context:
{context}

Question:
{question}

Explain clearly.
"""

    answer = ask_llama(prompt)

    return jsonify({"answer": answer})


@app.route("/db_data")
def db_data():

    conn = sqlite3.connect("project_knowledge.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, calls FROM functions LIMIT 10")
    data = cursor.fetchall()

    conn.close()

    return jsonify({"data": data})


@app.route("/analyze_repo", methods=["POST"])
def analyze_repo():

    global index, texts

    repo_url = request.json["repo"]

    if os.path.exists("project_knowledge.db"):
        os.remove("project_knowledge.db")

    create_tables()

    if os.path.exists(PROJECT_FOLDER):
        os.system(f"rm -rf {PROJECT_FOLDER}")

    print("Cloning repo...")
    git.Repo.clone_from(repo_url, PROJECT_FOLDER)
    print("Repo cloned.")

    data = analyze_directory(PROJECT_FOLDER)

    for file in data:

        file_id = insert_file(file["file"])

        for func in file["functions"]:
            insert_function(file_id, func["function_name"], func["calls"])

        for cls in file["classes"]:
            for method in cls["methods"]:
                insert_function(file_id, method["function_name"], method["calls"])

    build_call_graph(PROJECT_FOLDER)

    index, texts = build_vector_store()

    return jsonify({"status": "Repository analyzed successfully"})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)