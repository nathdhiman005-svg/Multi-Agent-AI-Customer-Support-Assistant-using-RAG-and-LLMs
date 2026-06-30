from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.crews.support_crew import SupportCrew

router = APIRouter(prefix="/agent", tags=["agent"])
support_crew = SupportCrew()

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    intent: str
    response: str

@router.post("/chat", response_model=ChatResponse)
def agent_chat(request: ChatRequest):
    """
    Submit a customer query.
    1. The Llama 3.2 Intent Agent classifies the query.
    2. The specialized agent (Gemini or Ollama) handles the response using RAG.
    """
    try:
        # Step 1: Route the query
        intents = support_crew.route_query(request.query)
        
        # Step 2: Process with specialized agent(s)
        response_text = support_crew.process_query(request.query, intents)
        
        return ChatResponse(intent=", ".join(intents), response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
