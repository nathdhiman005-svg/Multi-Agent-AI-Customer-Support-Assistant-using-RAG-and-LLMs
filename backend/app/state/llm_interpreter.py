import json
from app.config.llm_config import get_ollama_llm

class LLMInterpreter:
    def __init__(self):
        # We instantiate the LLM defined in config, explicitly using gemma3:4b
        self.llm = get_ollama_llm(model_name="gemma3:4b")

    def interpret(self, message: str, current_state: dict) -> list:
        """
        Uses an LLM to interpret the message into Semantic Events.
        Strictly returns a JSON array of event objects.
        """
        prompt = f"""You are a dialogue state event extractor.
You must output a raw JSON array of semantic events based on the user's message.
- You can and should extract MULTIPLE events if the user's message contains multiple distinct intents or issues.
- The output MUST ALWAYS be a JSON array (e.g. [{{...}}]), even if there is only one event.
- Do NOT output explanations, markdown formatting, reasoning, or conversational text.
- ONLY output events from the Allowed Events list below.
If no events apply, output an empty array [].

Allowed events:
- {{"event": "REFUND_REQUESTED"}}
- {{"event": "ISSUE_OPENED", "issue": "<description>"}}
- {{"event": "ISSUE_RESOLVED", "issue": "<description>"}}
- {{"event": "INTENT_CHANGED", "intent": "<intent_name>"}}

Current State Context (read-only):
{json.dumps(current_state, indent=2)}

User Message: {message}

JSON Array Output:"""

        try:
            response = self.llm.call([{"role": "user", "content": prompt}])
            
            # Clean response if it contains markdown code blocks
            text = response.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            events = json.loads(text)
            if not isinstance(events, list):
                return []
            return events
        except Exception:
            # If the LLM completely fails (timeout, JSON error, connection error), return empty array
            return []
