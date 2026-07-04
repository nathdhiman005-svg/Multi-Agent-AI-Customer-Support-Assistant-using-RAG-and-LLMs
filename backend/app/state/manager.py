from sqlalchemy.orm import Session
from app.models.state import DialogueState, get_default_state
from .extractor import EntityExtractor
from .normalizer import EntityNormalizer
from .rules_engine import StateRulesEngine
from .merge_engine import StateMergeEngine
from .state_validator import StateValidator
from .llm_interpreter import LLMInterpreter
from .llm_validator import LLMValidator

class DialogueStateManager:
    def __init__(self, db: Session):
        self.db = db
        self.extractor = EntityExtractor()
        self.normalizer = EntityNormalizer()
        self.rules_engine = StateRulesEngine()
        self.merge_engine = StateMergeEngine()
        self.state_validator = StateValidator()
        self.llm_interpreter = LLMInterpreter()
        self.llm_validator = LLMValidator()

    def get_or_create_state(self, user_email: str) -> DialogueState:
        """Retrieves existing state or creates a valid default state if none exists."""
        state = self.db.query(DialogueState).filter(DialogueState.user_email == user_email).first()
        if not state:
            state = DialogueState(
                user_email=user_email,
                state_data=get_default_state()
            )
            self.db.add(state)
            self.db.flush()
        return state

    def process_message(self, user_email: str, message: str, semantic_events: list = None) -> DialogueState:
        """
        Orchestrates the pre-processing pipeline.
        Note: semantic_events will be passed by the LLM Interpreter in Phase 3.
        """
        state = self.get_or_create_state(user_email)
        state_data = state.state_data

        # 1. Extraction & Normalization
        extracted_entities = self.extractor.extract(message)
        normalized_entities = self.normalizer.normalize(extracted_entities)

        # 2. Business Rules & LLM Intake
        if semantic_events is None:
            raw_events = self.llm_interpreter.interpret(message, state_data)
            events = self.llm_validator.validate(raw_events)
        else:
            events = self.llm_validator.validate(semantic_events)
            
        state_updates = self.rules_engine.apply_rules(state_data, normalized_entities, events)

        # 3. Merging
        new_state_data = self.merge_engine.merge(state_data, state_updates)

        # 4. Final Validation
        if self.state_validator.validate(new_state_data):
            state.state_data = new_state_data
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(state, "state_data")
            self.db.flush()
        else:
            raise ValueError("Invalid Dialogue State produced by pipeline.")

        return state
