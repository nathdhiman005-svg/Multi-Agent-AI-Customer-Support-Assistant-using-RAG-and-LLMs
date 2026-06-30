import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.rag.document_loader import process_knowledge_base
from app.rag.vector_store import query_knowledge_base

router = APIRouter(prefix="/rag", tags=["rag"])

KB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../knowledge_base")

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

@router.get("/files")
def list_files():
    """
    List all documents currently in the knowledge base directory.
    """
    if not os.path.exists(KB_DIR):
        os.makedirs(KB_DIR)
    
    files = [f for f in os.listdir(KB_DIR) if os.path.isfile(os.path.join(KB_DIR, f))]
    return {"files": files}

@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    """
    Upload a new document to the knowledge base and trigger a re-index.
    """
    if not os.path.exists(KB_DIR):
        os.makedirs(KB_DIR)
        
    file_path = os.path.join(KB_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
            
        # Re-index the knowledge base
        process_result = process_knowledge_base()
        
        return {
            "message": f"Successfully uploaded {file.filename}",
            "index_result": process_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/file/{filename}")
def delete_file(filename: str):
    """
    Delete a document from the knowledge base and trigger a re-index.
    """
    file_path = os.path.join(KB_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        os.remove(file_path)
        # Re-index the knowledge base
        process_result = process_knowledge_base()
        
        return {
            "message": f"Successfully deleted {filename}",
            "index_result": process_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
