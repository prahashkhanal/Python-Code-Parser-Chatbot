# 🚀 Python Code Parser Chatbot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg">
  <img src="https://img.shields.io/badge/Framework-Flask-green">
  <img src="https://img.shields.io/badge/Database-SQLite-lightgrey">
  <img src="https://img.shields.io/badge/Status-Active-success">
  <img src="https://img.shields.io/badge/License-Academic-orange">
</p>

<p align="center">
  <b>🔍 Analyze Code • 🤖 Chat with Codebase • 📊 Visualize Dependencies</b>
</p>

---

## ✨ Overview

**Python Code Parser Chatbot** is an intelligent system that:
- Parses Python code using AST  
- Builds dependency & call graphs  
- Uses **RAG (Retrieval-Augmented Generation)**  
- Allows users to **query code like a chatbot**

---

## 🎯 Key Features

✨ **AST-Based Parsing** – Deep code understanding  
🔗 **Dependency Mapping** – Tracks relationships between modules  
📊 **Call Graph Visualization** – Visual representation of execution  
🤖 **AI Chatbot (RAG)** – Ask questions about code  
💾 **SQLite Storage** – Efficient local database  
🌐 **Flask Web App** – Simple UI for interaction  
📄 **Auto Documentation Generator**

---
## 🏗️ Project Structure
Python-Code-Parser-Chatbot/
│
├── app.py
├── web_app.py
├── config.py
├── requirements.txt
├── project_knowledge.db
│
├── parser/
├── rag/
├── storage/
├── generator/
├── templates/
├── static/

---

## ⚙️ Tech Stack

| Category        | Technology |
|----------------|-----------|
| Language       | Python |
| Backend        | Flask |
| Parsing        | AST |
| Database       | SQLite |
| AI Layer       | RAG |
| Visualization  | Graph Builder |

---

## ⚡ Installation

### 1️⃣ Clone Repository

```bash
git clone <your-repo-url>
cd Python-Code-Parser-Chatbot
2️⃣ Create Virtual Environment
python -m venv venv
Activate:
Windows
venv\Scripts\activate
Mac/Linux
source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
▶️ Run the Project
🔹 Run Backend
python app.py
🔹 Run Web App (Recommended)
python web_app.py
🌐 Open in browser:
http://127.0.0.1:5000
🧠 How It Works



🗄️ Database
SQLite Database: project_knowledge.db
Stores:
Parsed code
Embeddings
Metadata
📄 Documentation Generator
python generator/doc_generator.py
💡 Example Queries
💬 "Explain this function"
💬 "Show dependencies of module"
💬 "What does this class do?"
🛠️ Troubleshooting
❌ Module Errors
pip install -r requirements.txt
❌ Port Issue
Change in web_app.py:
app.run(port=5001)
❌ Database Reset
rm project_knowledge.db
(Windows → del project_knowledge.db)
🔮 Future Scope
🚀 Multi-language support
🎨 Better UI/UX
🤝 Collaboration features
📊 Advanced visual graphs
🤝 Contributing
Contributions are welcome!
# Fork repo
# Create branch
git checkout -b feature-name
# Commit changes
git commit -m "Added feature"
# Push
git push origin feature-name
👨‍💻 Author
Your Name
📜 License
This project is for academic and educational purposes.
<p align="center"> ⭐ If you like this project, give it a star! </p> ```