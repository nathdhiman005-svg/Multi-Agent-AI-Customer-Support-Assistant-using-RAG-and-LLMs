from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from app.rag.vector_store import query_knowledge_base

class RAGSearchInput(BaseModel):
    query: str = Field(..., description="The query to search the knowledge base for. E.g., 'What is the refund policy?'")

class RAGSearchTool(BaseTool):
    name: str = "Knowledge_Base_Search"
    description: str = (
        "Search the company knowledge base for policies, manuals, and troubleshooting guides. "
        "Input should be a clear question or keywords."
    )
    args_schema: type[BaseModel] = RAGSearchInput

    def _run(self, query: str) -> str:
        results = query_knowledge_base(query)
        if not results or not results['documents'] or not results['documents'][0]:
            return "No relevant information found in the knowledge base."
        
        # Combine the chunks into a single text block
        chunks = results['documents'][0]
        sources = [meta.get('source', 'Unknown') for meta in results['metadatas'][0]]
        
        formatted_results = ""
        for i in range(len(chunks)):
            formatted_results += f"--- Source: {sources[i]} ---\n{chunks[i]}\n\n"
        
        return formatted_results
