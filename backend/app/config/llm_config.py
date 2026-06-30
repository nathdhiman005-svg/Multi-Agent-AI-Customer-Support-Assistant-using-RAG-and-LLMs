import os
from crewai import LLM
from dotenv import load_dotenv

load_dotenv()



def get_ollama_llm(model_name: str = "phi3"):
    """Specialized Agents (Billing, FAQ): Lightweight Local Model via Ollama"""
    return LLM(
        model="ollama/" + model_name,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.3
    )
