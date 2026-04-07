# AI Document Chatbot RAG

A document question-answering app that lets you upload a PDF and ask questions against its contents. The backend uses Flask, LangChain, FAISS, and Ollama for retrieval-augmented generation, while the frontend provides a simple chat interface.

## Project Structure

```text
frontend/
  index.html
  script.js
  styles.css
rag-ollama/
  app.py
  rag.py
  requirements.txt
  uploads/
```

## Features

- Upload PDF documents for indexing
- Ask natural-language questions about the document
- Uses Ollama for both the chat model and embeddings
- Returns answers based on retrieved PDF chunks

## Requirements

- Python 3.10+
- Ollama installed and running locally
- A supported Ollama model available, such as `llama3`

## Setup

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install backend dependencies.

```powershell
pip install -r rag-ollama/requirements.txt
```

3. Start Ollama and pull a model if needed.

```powershell
ollama serve
ollama pull llama3
```

## Run the App

From the project root:

```powershell
python rag-ollama/app.py
```

Then open the app in your browser at:

```text
http://127.0.0.1:5000
```

## Environment Variables

You can change the default behavior with these optional variables:

- `OLLAMA_HOST` - Ollama server URL, default `http://127.0.0.1:11434`
- `OLLAMA_MODEL` - chat model name, default `llama3`
- `OLLAMA_EMBEDDING_MODEL` - embedding model name, default same as `OLLAMA_MODEL`
- `RAG_PDF_PATH` - path to a default PDF to index on startup

## Usage

1. Upload a PDF using the file icon.
2. Wait for indexing to finish.
3. Ask questions in the chat box.
4. Use Clear conversation to reset the chat view.

## Notes

- Uploaded PDFs are stored in `rag-ollama/uploads/`.
- The backend serves the frontend directly, so you do not need to run a separate frontend server.
- If Ollama is unavailable, the app will fail to index or answer questions until the Ollama service is running.
