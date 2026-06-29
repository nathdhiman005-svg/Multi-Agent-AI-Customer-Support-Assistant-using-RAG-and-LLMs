from fastapi import APIRouter
from app.rag.document_loader import process_knowledge_base
from app.rag.vector_store import query_knowledge_base

router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/index")
def index_documents():
    """
    Scans the knowledge_base/ directory, processes PDFs, and loads them into ChromaDB.
    """
    result = process_knowledge_base()
    return result

@router.get("/search")
def search(query: str, n_results: int = 3):
    """
    Queries the vector database for relevant chunks of information.
    """
    results = query_knowledge_base(query, n_results)
    return {"results": results}
