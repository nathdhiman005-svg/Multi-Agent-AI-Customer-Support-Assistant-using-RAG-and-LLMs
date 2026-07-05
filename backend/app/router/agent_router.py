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
            # Fix Architectural Violation: Use Dialogue State instead of Conversation History
            manager = DialogueStateManager(db)
            state_obj = manager.get_or_create_state(current_user.email)
            active_issues = state_obj.state_data.get("conversation", {}).get("active_issues", [])
            summary = ", ".join(active_issues) if active_issues else "Customer requested escalation."
            
            # Trigger email agent asynchronously
            background_tasks.add_task(support_crew.run_email_agent_async, current_user.email, current_user.email, summary)
            
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
            
            # Step 4: Deterministic Human Escalation
            requires_human = state_obj.state_data.get("workflow", {}).get("requires_human", False)
            
            ESCALATION_MSG = "\n\nIf these steps are not resolving your issue, you can escalate this issue to our Human Support Team.\n\nWould you like me to forward this conversation to a human support representative?\n\nReply with 'Yes' if you would like to continue."
            
            if requires_human:
                if "If these steps are not resolving your issue" not in response_text:
                    response_text += ESCALATION_MSG
        
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
