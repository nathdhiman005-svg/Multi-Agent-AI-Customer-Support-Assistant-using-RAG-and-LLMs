from fastapi import FastAPI
from app.models.base import Base
from app.database.session import engine
from app.auth.router import router as auth_router
from app.rag.router import router as rag_router

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Customer Support AI Backend",
    description="Multi-Agent AI Customer Support System API",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(rag_router)

@app.get("/")
def root():
    return {"message": "Customer Support AI Backend is running"}
