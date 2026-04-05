from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import Ollama

def create_db(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    docs = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings()
    db = FAISS.from_documents(docs, embeddings)

    return db

def ask_question(db, question):
    docs = db.similarity_search(question)

    context = "\n".join([doc.page_content for doc in docs])

    llm = Ollama(model="llama3")

    prompt = f"""
You are a helpful assistant.
Answer ONLY using the context below.

Context:
{context}

Question:
{question}
"""

    response = llm(prompt)
    return response