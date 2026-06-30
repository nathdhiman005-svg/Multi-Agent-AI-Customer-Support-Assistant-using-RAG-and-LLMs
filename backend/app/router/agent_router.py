import os
import time
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.crews.support_crew import SupportCrew
from app.auth.router import get_current_user
from app.models.user import User
from app.database.session import get_db
from app.models.analytics import ConversationLog, Feedback

router = APIRouter(prefix="/agent", tags=["agent"])
support_crew = SupportCrew()

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    intent: str
    response: str
    conversation_id: int

class FeedbackRequest(BaseModel):
    conversation_id: int
    score: int  # 1 for thumbs up, -1 for thumbs down

@router.post("/chat", response_model=ChatResponse)
def agent_chat(request: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Submit a customer query. Requires authentication.
    Logs interaction to DB.
    """
    start_time = time.time()
    try:
        # Step 1: Route the query
        intents = support_crew.route_query(request.query)
        
        # Step 2: Process with specialized agent(s)
        response_text = support_crew.process_query(request.query, intents, current_user.email)
        
        # Calculate response time
        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000.0
        
        # Step 3: Log to Database
        log_entry = ConversationLog(
            user_email=current_user.email,
            query=request.query,
            response=response_text,
            intent=", ".join(intents),
            sentiment_score="N/A",  # Sentiment analysis disabled
            response_time_ms=elapsed_ms
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        return ChatResponse(intent=", ".join(intents), response=response_text, conversation_id=log_entry.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
def submit_feedback(request: FeedbackRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Submit user feedback (thumbs up/down) for a specific conversation.
    """
    log_entry = db.query(ConversationLog).filter(ConversationLog.id == request.conversation_id).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    feedback = Feedback(
        conversation_id=request.conversation_id,
        satisfaction_score=request.score
    )
    db.add(feedback)
    db.commit()
    return {"message": "Feedback recorded successfully"}
