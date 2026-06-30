from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class ConversationLog(Base):
    __tablename__ = "conversation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    intent = Column(String, nullable=False)
    sentiment_score = Column(String, nullable=True) # e.g. Positive, Neutral, Negative
    response_time_ms = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    feedbacks = relationship("Feedback", back_populates="conversation")

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversation_logs.id"))
    satisfaction_score = Column(Integer, nullable=False) # 1 for Up, -1 for Down
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("ConversationLog", back_populates="feedbacks")
