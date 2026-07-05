import chromadb
from chromadb.utils import embedding_functions
import os

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

def query_knowledge_base(query_text: str, n_results: int = 7, max_distance: float = 0.6):
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    filtered_results = {
        'ids': [[]],
        'distances': [[]],
        'metadatas': [[]],
        'documents': [[]]
    }
    
    if results.get('distances') and len(results['distances'][0]) > 0:
        for i in range(len(results['distances'][0])):
            if results['distances'][0][i] <= max_distance:
                filtered_results['ids'][0].append(results['ids'][0][i])
                filtered_results['distances'][0].append(results['distances'][0][i])
                filtered_results['metadatas'][0].append(results['metadatas'][0][i])
                filtered_results['documents'][0].append(results['documents'][0][i])
                
    return filtered_results

def delete_documents_by_source(filename: str):
    """Deletes all chunks from ChromaDB that came from a specific file."""
    collection.delete(
        where={"source": filename}
    )
