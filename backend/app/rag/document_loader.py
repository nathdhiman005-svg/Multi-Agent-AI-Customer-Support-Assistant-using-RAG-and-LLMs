import os
import uuid
from pypdf import PdfReader
from app.rag.vector_store import add_documents_to_collection

from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_split_pdf(file_path: str, chunk_size: int = 1000, overlap: int = 100):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
            
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    return chunks

def process_knowledge_base(kb_dir: str = "../knowledge_base"):
    # Resolve absolute path relative to the backend folder
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    target_dir = os.path.join(base_dir, "knowledge_base")

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        return {"status": "created_directory", "message": f"Created {target_dir}. Please add PDFs."}
        
    processed_files = []
    for filename in os.listdir(target_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(target_dir, filename)
            chunks = load_and_split_pdf(file_path)
            
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({"source": filename, "chunk": i})
                ids.append(f"{filename}_{i}_{uuid.uuid4().hex[:8]}")
                
            add_documents_to_collection(documents, metadatas, ids)
            processed_files.append({"filename": filename, "chunks": len(chunks)})
            
    return {"status": "success", "processed_files": processed_files}
