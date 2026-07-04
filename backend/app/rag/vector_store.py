import chromadb
from chromadb.utils import embedding_functions
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", os.path.join(BASE_DIR, "chroma_db"))

# Use a lightweight sentence-transformers model
# This will download the model the first time it runs
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_or_create_collection(name="knowledge_base", embedding_function=sentence_transformer_ef)

def add_documents_to_collection(documents: list[str], metadatas: list[dict], ids: list[str]):
    if not documents:
        return
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

def query_knowledge_base(query_text: str, n_results: int = 3):
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return results

def delete_documents_by_source(filename: str):
    """Deletes all chunks from ChromaDB that came from a specific file."""
    collection.delete(
        where={"source": filename}
    )
