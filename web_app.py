from flask import Flask, request, jsonify, render_template
from rag.embedder import build_vector_store, search
from parser.ast_parser import analyze_directory
from parser.graph_builder import build_call_graph
from storage.database import create_tables, insert_file, insert_function
import requests
import os
import git
import sqlite3
import threading

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
PROJECT_FOLDER = "analyzed_repo"

# Global state for analysis progress
analysis_state = {"status": "idle", "progress": 0}

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
You are explaining a Python project to a new developer. Use clear formatting with proper structure, like this example:

Functions: {functions}
Flow: {flow_text}

GENERATE YOUR RESPONSE EXACTLY IN THIS FORMAT WITH THESE RULES:

**PROJECT SUMMARY**

Write 2-3 sentences max explaining what this project does. Be concise and direct.

**KEY FUNCTIONS**

• function_name: One-line description of what it does
• function_name: One-line description of what it does
• function_name: One-line description of what it does

Keep each to ONE line. Make it scannable.

**EXECUTION FLOW**

1. First step - describe what happens
2. Second step - describe what happens
3. Third step - describe what happens

Use numbered steps (not arrows). Each step should be 1-2 sentences max.

IMPORTANT FORMATTING RULES:
- Use bold headers with ** **
- Use bullet points with • for lists
- Use numbered lists for steps
- Keep sentences short and punchy
- Avoid run-on explanations
- Add blank lines between sections
- Write for someone learning to code, not an expert
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
You are a helpful software engineer explaining code to a developer. Format your response clearly and concisely.

Code Context:
{context}

Question:
{question}

RESPOND FOLLOWING THESE FORMATTING RULES:

1. **Direct Answer First** - Start with a clear, direct answer to the question in 1-2 sentences
2. **Use Clean Structure**:
   - Use **bold headers** for sections
   - Use bullet points (•) for lists and key points
   - Use numbered lists (1, 2, 3...) for steps/processes
3. **Keep It Scannable** - Avoid long paragraphs, break into shorter lines
4. **Include Examples** - Show code snippets from the context if relevant
5. **Simple Language** - Explain like you're teaching a junior developer

Format expectations:
- Blank lines between sections
- One idea per bullet point or step
- Maximum 5-7 lines per section
- Short, punchy sentences

Write your answer now:
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


@app.route("/analysis_status")
def analysis_status():
    """Check the status of ongoing analysis"""
    return jsonify(analysis_state)


@app.route("/generate_flowchart")
def generate_flowchart():
    """Generate an intelligent, project-specific workflow diagram"""
    
    conn = sqlite3.connect("project_knowledge.db")
    cursor = conn.cursor()
    
    # Fetch all functions with their calls
    cursor.execute("SELECT name, calls FROM functions")
    functions_data = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM functions")
    total_functions = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT file_id) FROM functions")
    total_files = cursor.fetchone()[0]
    
    conn.close()
    
    if not functions_data:
        return jsonify({"error": "No data available"})
    
    try:
        # Analyze function names to categorize them
        api_funcs = []
        data_funcs = []
        util_funcs = []
        process_funcs = []
        
        for func_name, calls in functions_data:
            if not func_name:
                continue
            
            name_lower = func_name.lower()
            
            # Categorize based on function name patterns
            if any(x in name_lower for x in ['route', 'handler', 'endpoint', 'api', 'get', 'post', 'request']):
                api_funcs.append(func_name[:25])
            elif any(x in name_lower for x in ['parse', 'analyze', 'extract', 'process', 'build', 'generate']):
                process_funcs.append(func_name[:25])
            elif any(x in name_lower for x in ['db', 'database', 'store', 'save', 'fetch', 'query', 'insert']):
                data_funcs.append(func_name[:25])
            elif any(x in name_lower for x in ['util', 'helper', 'format', 'convert', 'clean', 'validate']):
                util_funcs.append(func_name[:25])
            else:
                process_funcs.append(func_name[:25])
        
        # Create dynamic workflow based on what we found
        flowchart_lines = ["flowchart TD"]
        
        if api_funcs:
            flowchart_lines.append('    A["📨 API/Entry Points<br/>' + ', '.join(api_funcs[:3]) + '"]')
        else:
            flowchart_lines.append('    A["📨 Entry Points"]')
        
        if process_funcs:
            flowchart_lines.append('    B["⚙️ Core Processing<br/>' + ', '.join(process_funcs[:3]) + '"]')
        else:
            flowchart_lines.append('    B["⚙️ Processing"]')
        
        if data_funcs:
            flowchart_lines.append('    C["💾 Data Management<br/>' + ', '.join(data_funcs[:3]) + '"]')
        else:
            flowchart_lines.append('    C["💾 Data Management"]')
        
        if util_funcs:
            flowchart_lines.append('    D["🛠️ Utilities<br/>' + ', '.join(util_funcs[:2]) + '"]')
        else:
            flowchart_lines.append('    D["🛠️ Utilities"]')
        
        flowchart_lines.append('    E["✅ Output/Results"]')
        
        # Add main flow connections
        flowchart_lines.append('    A --> B')
        flowchart_lines.append('    B --> C')
        flowchart_lines.append('    C --> E')
        
        # Add support connections
        if util_funcs:
            flowchart_lines.append('    B -.->|Uses| D')
            flowchart_lines.append('    C -.->|Uses| D')
        
        # Count major components found
        components = sum([1 for x in [api_funcs, process_funcs, data_funcs, util_funcs] if x])
        
        mermaid_code = "\n".join(flowchart_lines)
        
        # Generate description with actual findings
        description = f"""
        <div style="background: rgba(56, 189, 248, 0.1); border-left: 4px solid #38bdf8; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
            <h4 style="color: #38bdf8; margin: 0 0 10px 0;">📖 Project Architecture Overview</h4>
            <p style="color: #cbd5e1; margin: 0 0 8px 0;">
                <strong>Project Stats:</strong> <strong>{total_functions} functions</strong> organized into <strong>{components} major components</strong> across <strong>{total_files} files</strong>.
            </p>
            <p style="color: #cbd5e1; margin: 0 0 8px 0;">
                <strong>Architecture:</strong>
                {'✓ API/Entry Points - Handles requests' if api_funcs else ''}
                {'✓ Core Processing - Main business logic' if process_funcs else ''}
                {'✓ Data Management - Database & storage' if data_funcs else ''}
                {'✓ Utilities - Helper functions' if util_funcs else ''}
            </p>
            <p style="color: #cbd5e1; margin: 0 0 0px 0;">
                <strong>Flow:</strong> Requests enter through entry points → processed by core logic → interact with data layer → utilities support throughout → results returned. This structure keeps code organized and maintainable.
            </p>
        </div>
        """
        
        return jsonify({"flowchart": mermaid_code, "description": description})
        
    except Exception as e:
        print(f"Flowchart generation error: {e}")
        return jsonify({"error": f"Failed to generate flowchart: {str(e)}"})




@app.route("/analyze_repo", methods=["POST"])
def analyze_repo():

    global index, texts, analysis_state

    repo_url = request.json["repo"]
    
    # Start background task
    def process_repo():
        global index, texts, analysis_state
        
        try:
            analysis_state = {"status": "Cloning repository...", "progress": 10}
            
            if os.path.exists("project_knowledge.db"):
                os.remove("project_knowledge.db")

            create_tables()

            if os.path.exists(PROJECT_FOLDER):
                os.system(f"rm -rf {PROJECT_FOLDER}")

            git.Repo.clone_from(repo_url, PROJECT_FOLDER)
            
            analysis_state = {"status": "Parsing code...", "progress": 30}
            
            data = analyze_directory(PROJECT_FOLDER)

            for file in data:
                # Skip files with parsing errors
                if file.get("error"):
                    continue

                file_id = insert_file(file["file"])

                for func in file["functions"]:
                    insert_function(file_id, func["function_name"], func["calls"])

                for cls in file["classes"]:
                    for method in cls["methods"]:
                        insert_function(file_id, method["function_name"], method["calls"])

            analysis_state = {"status": "Building call graph...", "progress": 70}
            build_call_graph(PROJECT_FOLDER)

            analysis_state = {"status": "Building vector store...", "progress": 85}
            index, texts = build_vector_store()

            analysis_state = {"status": "completed", "progress": 100}
            print("✅ Repository analysis complete!")
            
        except Exception as e:
            analysis_state = {"status": f"Error: {str(e)}", "progress": 0}
            print(f"❌ Analysis error: {e}")

    # Start processing in background thread
    thread = threading.Thread(target=process_repo, daemon=True)
    thread.start()

    # Return immediately
    return jsonify({"status": "Analysis started. Processing in background..."})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data["message"]

    response = search(user_input)  # or your logic

    return jsonify({"response": response})