import os
import time
import re
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.crews.support_crew import SupportCrew
from app.auth.router import get_current_user
from app.models.user import User
from app.database.session import get_db
from app.models.analytics import ConversationLog, Feedback
from app.state.manager import DialogueStateManager
from app.state.state_formatter import StateFormatter

router = APIRouter(prefix="/agent", tags=["agent"])
support_crew = SupportCrew()
formatter = StateFormatter()

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
def agent_chat(request: ChatRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Submit a customer query. Requires authentication.
    Logs interaction to DB.
    """
    start_time = time.time()
    try:
        user_query_clean = request.query.strip().lower()
        
        if user_query_clean in ["yes", "y", "yes.", "yes please", "yes!", "yes, i want to escalate"]:
            # Context Loss Fix: Fetch previous query from DB
            last_log = db.query(ConversationLog).filter(ConversationLog.user_email == current_user.email).order_by(ConversationLog.timestamp.desc()).first()
            summary = last_log.query if last_log else "Customer requested escalation for an unknown issue."
            
            # Trigger email agent asynchronously
            background_tasks.add_task(support_crew.run_email_agent_async, current_user.email, summary)
            
            response_text = "Your issue is taken by the human support team. Thank you for reaching out our customer support."
            intents = ["Escalation_Confirmed"]
            
        elif user_query_clean in ["no", "n", "no.", "no thanks", "no!"]:
            response_text = "We are happy to solve your issue. For further query don't hesitate to reach out."
            intents = ["Escalation_Declined"]
            
        else:
            # Step 1: Process through Dialogue State Manager
            manager = DialogueStateManager(db)
            state_obj = manager.process_message(current_user.email, request.query)
            
            # Format the state
            formatted_state = formatter.format(state_obj.state_data)
            
            # Step 2: Route the query using the dialogue state
            intents = support_crew.route_query(request.query, formatted_state)
            
            # Step 3: Process with specialized agent(s) passing the dialogue state and user_email
            response_text = support_crew.process_query(request.query, formatted_state, intents, current_user.email)
        
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
        db.rollback()
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

@router.get("/logs")
def get_conversation_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Fetch all conversation logs and their associated feedback for the admin dashboard.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    logs = db.query(ConversationLog).order_by(ConversationLog.timestamp.desc()).all()
    feedbacks = db.query(Feedback).all()
    
    # Map feedback to logs
    feedback_map = {f.conversation_id: f.satisfaction_score for f in feedbacks}
    
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "user_email": log.user_email,
            "query": log.query,
            "response": log.response,
            "intent": log.intent,
            "response_time_ms": log.response_time_ms,
            "timestamp": log.timestamp.isoformat(),
            "feedback": feedback_map.get(log.id, None)
        })
        
    return {"logs": result}
