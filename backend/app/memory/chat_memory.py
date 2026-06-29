from sqlalchemy.orm import Session
from app.models.session import ChatSession
from app.models.message import Message
import uuid

def create_chat_session(db: Session, user_id: int | None = None):
    session_token = str(uuid.uuid4())
    db_session = ChatSession(user_id=user_id, session_token=session_token)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_chat_session(db: Session, session_token: str):
    return db.query(ChatSession).filter(ChatSession.session_token == session_token).first()

def add_message_to_session(db: Session, session_id: int, sender_type: str, content: str):
    db_message = Message(session_id=session_id, sender_type=sender_type, content=content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_session_messages(db: Session, session_id: int, limit: int = 50):
    return db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).limit(limit).all()
