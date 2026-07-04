from sqlalchemy import Column, Integer, String, JSON
from app.models.base import Base

def get_default_state():
    return {
        "customer": {
            "sentiment": "Neutral",
            "refund_requested": False,
            "escalation_offered": False
        },
        "entities": {
            "current_product": None,
            "product_id": None,
            "order_id": None,
            "payment_method": None,
            "email_address": None
        },
        "conversation": {
            "previous_intent": None,
            "current_intent": "General Inquiry",
            "active_issues": [],
            "resolved_issues": []
        },
        "workflow": {
            "requires_human": False,
            "department_handoff": None
        },
        "metadata": {
            "version": "1.0"
        }
    }

class DialogueState(Base):
    __tablename__ = "dialogue_states"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, unique=True, index=True, nullable=False)
    state_data = Column(JSON, nullable=False, default=get_default_state)
