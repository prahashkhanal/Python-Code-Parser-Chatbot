git# AI Code Documentation Assistant - Setup & Run Guide

## Prerequisites

You need to have **Ollama** running locally with the **phi3** model installed.

### Install Ollama
1. Download Ollama from: https://ollama.ai
2. Install and run it
3. Pull the phi3 model:
   ```bash
   ollama pull phi3
   ```
4. Start Ollama (it should run on `http://localhost:11434`)

## Step-by-Step Setup

### 1. Clone/Navigate to Project
```bash
cd /home/prahash/ai_doc_system
```

### 2. Create Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Ollama is Running
```bash
curl http://localhost:11434/api/tags
```
You should see the phi3 model listed.

## Running the Application

### Option 1: Run Web Application (Recommended)
```bash
# Make sure venv is activated
source venv/bin/activate

# Run the web app
python web_app.py
```

The application will start at: **http://localhost:5000**

### Option 2: Analyze a Local Project First
```bash
# Make sure venv is activated
source venv/bin/activate

# This analyzes the sample_project and stores data
python app.py
```

Then run the web app:
```bash
python web_app.py
```

## Usage

### Via Web Interface (http://localhost:5000)

1. **Analyze Repository**
   - Enter a GitHub URL (e.g., `https://github.com/user/repo`)
   - Click "Analyze"
   - Wait for the repository to be cloned, parsed, and indexed

2. **View Project Insight**
   - Click "Generate Explanation"
   - AI will generate a summary of the project

3. **Ask Questions**
   - Type any question about the code
   - Click "Ask"
   - AI will answer based on the code context

4. **View Visualizations**
   - **Call Graph**: Shows function dependencies
   - **Database**: Shows all parsed functions and their dependencies

## Troubleshooting

### Issue: "Connection refused" on Ollama
**Solution**: Make sure Ollama is running in the background:
```bash
ollama serve
```

### Issue: "phi3" model not found
**Solution**: Pull the model:
```bash
ollama pull phi3
```

### Issue: Repository analysis fails
**Solution**: Ensure git is installed:
```bash
sudo apt-get install git  # Linux
brew install git          # macOS
```

### Issue: Dependencies not installed
**Solution**: Reinstall requirements:
```bash
pip install --upgrade -r requirements.txt
```

## Project Structure

```
ai_doc_system/
├── web_app.py              # Main Flask application
├── app.py                  # Offline analysis script
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Web interface (improved UI)
├── parser/
│   ├── ast_parser.py      # Code parsing
│   ├── graph_builder.py   # Call graph generation
│   └── dependency_mapper.py
├── rag/
│   ├── embedder.py        # Vector embeddings
│   └── retriever.py       # RAG retrieval
├── storage/
│   └── database.py        # SQLite database
└── static/
    └── call_graph.png     # Generated graph visualization
```

## Features

✅ **Repository Analysis**: Clone and analyze GitHub repositories  
✅ **Code Parsing**: Extract functions, classes, and dependencies using AST  
✅ **Call Graph**: Visualize function call relationships  
✅ **Vector Database**: Semantic search with embeddings  
✅ **AI Q&A**: Ask questions about the code using Ollama + phi3  
✅ **Project Insights**: Auto-generated project documentation  
✅ **Modern UI**: Clean, responsive web interface  

## Performance Tips

- First analysis may take 2-3 minutes (downloading embeddings)
- Large repositories (1000+ files) may take longer
- AI responses depend on Ollama performance
- Keep Ollama running in the background for best experience

## Database

The application uses SQLite (`project_knowledge.db`) to store:
- File information
- Function names
- Function calls/dependencies
- Metadata

The database is automatically created and populated during analysis.

---

For issues or questions, check the backend logs in the terminal running `python web_app.py`.
