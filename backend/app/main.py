from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from app.models.base import Base
from app.models.user import User
from app.models.analytics import ConversationLog, Feedback
from app.models.state import DialogueState, get_default_state
from app.database.session import engine, SessionLocal
from app.auth.router import router as auth_router
from app.rag.router import router as rag_router
from app.router.agent_router import router as agent_router

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Automatically seed default dialogue states for any existing users
def init_states():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            existing_state = db.query(DialogueState).filter(DialogueState.user_email == user.email).first()
            if not existing_state:
                new_state = DialogueState(
                    user_email=user.email,
                    state_data=get_default_state()
                )
                db.add(new_state)
        db.commit()
    except Exception as e:
        print(f"Error initializing states: {e}")
    finally:
        db.close()

init_states()

app = FastAPI(
    title="Customer Support AI Backend",
    description="Multi-Agent AI Customer Support System API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(rag_router)
app.include_router(agent_router)

frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/admin.html")
def admin_page():
    return FileResponse(os.path.join(frontend_path, "admin.html"))

@app.get("/admin.css")
def admin_css():
    return FileResponse(os.path.join(frontend_path, "admin.css"))

@app.get("/admin.js")
def admin_js():
    return FileResponse(os.path.join(frontend_path, "admin.js"))
