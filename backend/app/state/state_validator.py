class StateValidator:
    def validate(self, state: dict) -> bool:
        """Verifies that the Dialogue State strictly conforms to the JSON schema."""
        required_keys = ["customer", "entities", "conversation", "workflow", "metadata"]
        for key in required_keys:
            if key not in state:
                return False
                
        # Type checking
        if not isinstance(state["customer"].get("refund_requested"), bool):
            return False
            
        if not isinstance(state["conversation"].get("active_issues"), list):
            return False
            
        if not isinstance(state["conversation"].get("resolved_issues"), list):
            return False
            
        return True
