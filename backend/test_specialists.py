import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.state.manager import DialogueStateManager
from app.state.state_formatter import StateFormatter
from app.crews.support_crew import SupportCrew
from app.models.state import DialogueState

db = SessionLocal()
manager = DialogueStateManager(db)
formatter = StateFormatter()
crew = SupportCrew()

email = "specialist_test@example.com"

# Clean any existing state
existing = db.query(DialogueState).filter_by(user_email=email).first()
if existing:
    db.delete(existing)
    db.commit()

print("--- Testing Dialogue State Injection to Specialists ---")

# Step 1: Preload some state by having the user buy a NovaBook Pro
print("\n[User Message]: 'I bought a NovaBook Pro yesterday.'")
state_1 = manager.process_message(email, "I bought a NovaBook Pro yesterday.")

# Step 2: The actual ambiguous follow-up
msg_2 = "Can I return it?"
print(f"\n[User Message]: '{msg_2}'")
state_2 = manager.process_message(email, msg_2)
formatted_state = formatter.format(state_2.state_data)

print(f"\n[Formatted State Injected into Prompt]:\n{formatted_state}")

print("\n--- Executing CrewAI Specialists (Forced Billing) ---")
# We manually force categories to ['Billing'] to see if the Billing Agent 
# correctly identifies that "it" is a NovaBook Pro

# Print the EXACT prompt received by the Billing Agent
billing_agent = crew.agents.billing_support_agent()
billing_task = crew.tasks.billing_task(billing_agent, msg_2, formatted_state, email)
print("\n================ EXACT PROMPT SENT TO BILLING AGENT ================\n")
print(billing_task.description)
print("\n===================================================================\n")

result = crew.process_query(current_message=msg_2, dialogue_state=formatted_state, categories=["Billing"], user_email=email)

print("\n--- Output from Response Aggregator ---")
print(result)

db.close()
