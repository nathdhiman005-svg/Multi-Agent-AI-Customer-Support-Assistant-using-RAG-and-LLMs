import uuid
import sys
import traceback
from unittest.mock import patch
from sqlalchemy.orm import Session
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
    
    def get_state(email):
        return db.query(DialogueState).filter(DialogueState.user_email == email).first()
        
    def get_logs(email):
        return db.query(ConversationLog).filter(ConversationLog.user_email == email).all()

    print("=========================================")
    
    # Test 1: Normal execution
    email1 = f"test1_{uuid.uuid4()}@test.com"
    user1 = MockUser(email1)
    try:
        with patch('app.router.agent_router.support_crew.route_query', return_value=['Technical']), \
             patch('app.router.agent_router.support_crew.process_query', return_value='Success'):
            
            req = ChatRequest(query="My product is broken")
            agent_chat(req, bg_tasks, user1, db)
            
            s = get_state(email1)
            l = get_logs(email1)
            if s is not None and len(l) == 1:
                print("Test 1 (Normal Execution): PASS")
            else:
                print("Test 1 Failed: State or log missing")
    except Exception as e:
        print(f"Test 1 Failed with Exception: {e}")

    # Test 2: Force exception before Intent Router finishes
    email2 = f"test2_{uuid.uuid4()}@test.com"
    user2 = MockUser(email2)
    try:
        with patch('app.router.agent_router.support_crew.route_query', side_effect=Exception("Router Failed")):
            req = ChatRequest(query="Will fail")
            try:
                agent_chat(req, bg_tasks, user2, db)
            except HTTPException:
                pass # Expected
            
            # Since db.rollback() was called, the DialogueState shouldn't exist
            s = get_state(email2)
            l = get_logs(email2)
            if s is None and len(l) == 0:
                print("Test 2 (Force an exception before Intent Router finishes): PASS")
            else:
                print("Test 2 Failed: State leaked!")
    except Exception as e:
        print(f"Test 2 Failed with Exception: {e}")

    # Test 3 & 4 & 5: Force exception inside Specialist / Aggregator / LLM
    email3 = f"test3_{uuid.uuid4()}@test.com"
    user3 = MockUser(email3)
    try:
        with patch('app.router.agent_router.support_crew.route_query', return_value=['Technical']), \
             patch('app.router.agent_router.support_crew.process_query', side_effect=Exception("Specialist Failed")):
            req = ChatRequest(query="Will fail")
            try:
                agent_chat(req, bg_tasks, user3, db)
            except HTTPException:
                pass
            
            s = get_state(email3)
            l = get_logs(email3)
            if s is None and len(l) == 0:
                print("Test 3, 4, 5 (Specialist/Aggregator/LLM Exceptions): PASS")
            else:
                print("Test 3/4/5 Failed: State leaked!")
    except Exception as e:
        print(f"Test 3, 4, 5 Failed with Exception: {e}")
        
    # Test 6: Consecutive runs
    email6 = f"test6_{uuid.uuid4()}@test.com"
    user6 = MockUser(email6)
    try:
        with patch('app.router.agent_router.support_crew.route_query', return_value=['Technical']), \
             patch('app.router.agent_router.support_crew.process_query', return_value='Success'):
            
            req1 = ChatRequest(query="First")
            agent_chat(req1, bg_tasks, user6, db)
            
            s1 = get_state(email6)
            if s1 is None:
                print("Test 6 Failed: Missing state 1")
            
            req2 = ChatRequest(query="Second")
            agent_chat(req2, bg_tasks, user6, db)
            
            s2 = get_state(email6)
            l = get_logs(email6)
            if s2 is not None and len(l) == 2:
                print("Test 6 (Consecutive successful conversations): PASS")
            else:
                print("Test 6 Failed: State or logs missing on run 2")
    except Exception as e:
        print(f"Test 6 Failed with Exception: {e}")

    db.close()

if __name__ == "__main__":
    run_tests()
