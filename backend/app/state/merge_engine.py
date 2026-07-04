class StateMergeEngine:
    def merge(self, current_state: dict, updates: dict) -> dict:
        """Dumbly applies translated changes into the current state object."""
        # Deep copy to avoid mutating the original directly until validation passes
        import copy
        new_state = copy.deepcopy(current_state)
        
        for category, fields in updates.items():
            if category in new_state:
                for key, value in fields.items():
                    # Dumb merge: overwrite completely
                    new_state[category][key] = value
                    
        # Update metadata timestamp
        from datetime import datetime
        if "metadata" not in new_state:
            new_state["metadata"] = {}
        new_state["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        
        return new_state
