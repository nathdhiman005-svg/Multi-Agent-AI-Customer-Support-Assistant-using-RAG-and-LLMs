import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.state.manager import DialogueStateManager
from app.state.state_formatter import StateFormatter
from app.crews.support_crew import SupportCrew
from app.models.state import DialogueState

def run_test(test_name, user_email, messages):
    db = SessionLocal()
    manager = DialogueStateManager(db)
    formatter = StateFormatter()
    crew = SupportCrew()

    # Clean existing state
    existing = db.query(DialogueState).filter_by(user_email=user_email).first()
    if existing:
        db.delete(existing)
        db.commit()

    print(f"\n======================================")
    print(f"TEST: {test_name}")
    print(f"======================================")

    result = ""
    for msg in messages:
        print(f"\n[User]: {msg}")
        state_obj = manager.process_message(user_email, msg)
        formatted_state = formatter.format(state_obj.state_data)
        
        # Route query
        categories = crew.route_query(msg, formatted_state)
        print(f"[Router Selected]: {categories}")
        
        # Process query
        result = crew.process_query(msg, formatted_state, categories, user_email)
        print(f"\n[Aggregator Response]:\n{result}")

    db.close()
    return result

print("Starting Aggregator Tests...")

# 1. Product Switch
run_test("Product Switch", "test1@example.com", [
    "I bought a NovaBook Pro.",
    "Actually, I'm talking about my NovaPhone X."
])

# 2. Follow-up Context
run_test("Follow-up Context", "test2@example.com", [
    "My controller won't connect.",
    "It still doesn't work."
])

# 3. Billing Context
run_test("Billing Context", "test3@example.com", [
    "I bought a controller yesterday but it arrived broken. I want a refund."
])

# 4. Complaint Escalation
run_test("Complaint Escalation", "test4@example.com", [
    "My controller is completely broken.",
    "Your service is terrible, nothing works and I am extremely frustrated. I demand you fix this!"
])

# 5. Mixed Multi-Intent
run_test("Mixed Multi-Intent Conversation", "test5@example.com", [
    "I have a duplicate charge on my account, my Bluetooth won't connect, and I'm really angry about this whole situation!"
])
