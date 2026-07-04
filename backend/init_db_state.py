import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal, engine
from app.models.base import Base
from app.models.user import User
from app.models.state import DialogueState, get_default_state

# Ensure tables are created
Base.metadata.create_all(bind=engine)

def init_states():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        added_count = 0
        for user in users:
            existing_state = db.query(DialogueState).filter(DialogueState.user_email == user.email).first()
            if not existing_state:
                new_state = DialogueState(
                    user_email=user.email,
                    state_data=get_default_state()
                )
                db.add(new_state)
                added_count += 1
        db.commit()
        print(f"Successfully initialized states for {added_count} users.")
        
        # Test JSON read/write
        test_state = db.query(DialogueState).first()
        if test_state:
            print(f"Test Read Successful! Found state for: {test_state.user_email}")
            print(f"State Data: {test_state.state_data}")
        else:
            print("No states found in database.")
            
    except Exception as e:
        print(f"Error initializing states: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_states()
