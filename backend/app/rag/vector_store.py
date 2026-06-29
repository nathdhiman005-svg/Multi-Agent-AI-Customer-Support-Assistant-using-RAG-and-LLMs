import chromadb
from chromadb.utils import embedding_functions
import os

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

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
