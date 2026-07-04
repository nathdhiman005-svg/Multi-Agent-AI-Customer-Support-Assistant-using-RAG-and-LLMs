import uuid
from unittest.mock import patch
from app.database.session import SessionLocal
from app.models.state import DialogueState
from app.models.analytics import ConversationLog
from app.router.agent_router import agent_chat, ChatRequest
from app.models.user import User
from fastapi import BackgroundTasks, HTTPException

class MockUser:
    def __init__(self, email):
        self.email = email
        self.is_admin = False

def run_tests():
    db = SessionLocal()
    bg_tasks = BackgroundTasks()
    
    def get_logs(email):
        return db.query(ConversationLog).filter(ConversationLog.user_email == email).all()

    print("=========================================")
    
    # Test 1: Successful Conversation
    email1 = f"success_{uuid.uuid4()}@test.com"
    user1 = MockUser(email1)
    try:
        with patch('app.router.agent_router.support_crew.route_query', return_value=['Technical']), \
             patch('app.router.agent_router.support_crew.process_query', return_value='Mock Aggregator Success Response'):
            
            req = ChatRequest(query="My controller doesn't work.")
            response = agent_chat(req, bg_tasks, user1, db)
            
            logs = get_logs(email1)
            
            print(f"Test 1: Successful Conversation")
            print(f"-> Logs count: {len(logs)}")
            if len(logs) == 1:
                print(f"-> Persisted Log Response: '{logs[0].response}'")
                print(f"-> API Response: '{response.response}'")
                if logs[0].response == response.response:
                    print("-> Verification: Exact response returned to customer was persisted.")
                    print("PASS")
                else:
                    print("FAIL (Mismatch)")
            else:
                print("FAIL (No log created)")
                
    except Exception as e:
        print(f"Test 1 Failed with Exception: {e}")

    print("=========================================")
    
    # Test 2: Forced Failure
    email2 = f"fail_{uuid.uuid4()}@test.com"
    user2 = MockUser(email2)
    try:
        with patch('app.router.agent_router.support_crew.route_query', return_value=['Technical']), \
             patch('app.router.agent_router.support_crew.process_query', side_effect=Exception("Aggregator crashed!")):
            
            req = ChatRequest(query="Help me!")
            try:
                agent_chat(req, bg_tasks, user2, db)
            except HTTPException:
                pass # Expected failure
            
            logs = get_logs(email2)
            
            print(f"Test 2: Forced Failure (Exception inside CrewAI)")
            print(f"-> Logs count: {len(logs)}")
            if len(logs) == 0:
                print("-> Verification: No partial or empty ConversationLog was persisted.")
                print("PASS")
            else:
                print("FAIL (Log was erroneously persisted!)")
                
    except Exception as e:
        print(f"Test 2 Failed with Exception: {e}")

    db.close()

if __name__ == "__main__":
    run_tests()
