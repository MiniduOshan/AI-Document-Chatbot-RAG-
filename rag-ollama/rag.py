import os
import subprocess
import threading
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_PDF_PATH = Path(os.getenv("RAG_PDF_PATH", BASE_DIR / "sample.pdf"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
LLM_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", LLM_MODEL)

llm = None
embeddings = None
vector_db = None
current_pdf_path = DEFAULT_PDF_PATH
index_lock = threading.Lock()
indexing_in_progress = False
last_index_error = None
last_indexed_pdf = None


def is_ollama_available():
    try:
        with urlopen(f"{OLLAMA_HOST}/api/tags", timeout=2) as response:
            return response.status == 200
    except URLError:
        return False
    except Exception:
        return False


def start_ollama_server():
    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def ensure_ollama_server(timeout_seconds=30):
    if is_ollama_available():
        return

    try:
        start_ollama_server()
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Ollama is not installed or not available on PATH. Install Ollama and start the server."
        ) from exc

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if is_ollama_available():
            return
        time.sleep(1)

    raise RuntimeError(
        f"Ollama did not become available at {OLLAMA_HOST}. Start it manually with 'ollama serve'."
    )


def get_clients():
    global llm, embeddings
    ensure_ollama_server()

    if llm is None:
        llm = Ollama(model=LLM_MODEL)

    if embeddings is None:
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    return llm, embeddings


def set_pdf_source(pdf_path):
    global current_pdf_path, vector_db, last_index_error, last_indexed_pdf
    current_pdf_path = Path(pdf_path)
    vector_db = None
    last_index_error = None
    last_indexed_pdf = None


def get_pdf_source():
    return current_pdf_path


def get_index_status():
    return {
        "indexing": indexing_in_progress,
        "ready": vector_db is not None,
        "pdf": str(current_pdf_path),
        "indexed_pdf": str(last_indexed_pdf) if last_indexed_pdf else None,
        "error": last_index_error,
    }


# Load and process PDF
def create_vector_store(pdf_path=None):
    _, current_embeddings = get_clients()
    pdf_path = Path(pdf_path or current_pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found at '{pdf_path}'. Set RAG_PDF_PATH or place sample.pdf in rag-ollama/."
        )

    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = splitter.split_documents(documents)

    vectorstore = FAISS.from_documents(docs, current_embeddings)

    return vectorstore


def get_vector_store():
    global vector_db, last_index_error, last_indexed_pdf
    with index_lock:
        if vector_db is None:
            vector_db = create_vector_store()
            last_indexed_pdf = Path(current_pdf_path)
            last_index_error = None
    return vector_db


def warm_up_vector_store():
    global indexing_in_progress, last_index_error
    if indexing_in_progress:
        return

    indexing_in_progress = True
    try:
        get_vector_store()
        last_index_error = None
    except Exception as exc:
        last_index_error = str(exc)
        raise
    finally:
        indexing_in_progress = False


# Ask question
def ask_question(query):
    current_llm, _ = get_clients()
    if last_index_error:
        raise RuntimeError(f"Document indexing failed: {last_index_error}")

    db = get_vector_store()
    docs = db.similarity_search(query, k=3)

    if not docs:
        return "I could not find relevant content in the indexed document."

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
    Answer the question based ONLY on the context below.

    Context:
    {context}

    Question:
    {query}
    """

    response = current_llm.invoke(prompt)

    return response