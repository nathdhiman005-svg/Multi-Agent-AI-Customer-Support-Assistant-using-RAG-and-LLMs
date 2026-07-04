import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.config.llm_config import get_ollama_llm

llm = get_ollama_llm()
print(dir(llm))
try:
    print(llm.call([{"role": "user", "content": "say hi"}]))
except Exception as e:
    print("Call failed:", e)
