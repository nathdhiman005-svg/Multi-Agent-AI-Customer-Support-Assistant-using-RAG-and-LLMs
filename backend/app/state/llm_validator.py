class LLMValidator:
    def __init__(self):
        self.allowed_events = ["REFUND_REQUESTED", "ESCALATION_REQUESTED", "CUSTOMER_FRUSTRATED", "MANUAL_APPROVAL_REQUIRED", "TROUBLESHOOTING_FAILED", "SPECIALIST_ESCALATION_RECOMMENDED", "ISSUE_OPENED", "ISSUE_RESOLVED", "INTENT_CHANGED"]

    def validate(self, events: list) -> list:
        """
        Validates the structure of LLM-generated Semantic Events.
        Filters out hallucinations or invalid formats.
        """
        if not isinstance(events, list):
            return []

        valid_events = []
        for event in events:
            if not isinstance(event, dict):
                continue
                
            event_type = event.get("event")
            if not event_type or event_type not in self.allowed_events:
                continue
                
            if event_type in ["ISSUE_OPENED", "ISSUE_RESOLVED"] and not event.get("issue"):
                continue
                
            if event_type == "INTENT_CHANGED" and not event.get("intent"):
                continue
                
            valid_events.append(event)
            
        return valid_events
