class StateRulesEngine:
    def apply_rules(self, current_state: dict, entities: dict, events: list) -> dict:
        """Translates events and entities into state updates."""
        updates = {
            "customer": {},
            "entities": entities.copy(),
            "conversation": {},
            "workflow": {}
        }
        
        current_product = current_state.get("entities", {}).get("current_product")
        new_product = entities.get("current_product")
        
        # Product switch logic
        if new_product and current_product and new_product != current_product:
            # If changing product, clear active issues and mark as resolved
            active_issues = current_state.get("conversation", {}).get("active_issues", [])
            resolved_issues = current_state.get("conversation", {}).get("resolved_issues", [])
            
            # Safely combine without duplicates
            new_resolved = list(resolved_issues)
            for issue in active_issues:
                if issue not in new_resolved:
                    new_resolved.append(issue)
            
            updates["conversation"]["resolved_issues"] = new_resolved
            updates["conversation"]["active_issues"] = []
            
        for event in events:
            event_type = event.get("event")
            
            if event_type == "REFUND_REQUESTED":
                updates["customer"]["refund_requested"] = True
                
            elif event_type == "ISSUE_OPENED":
                issue = event.get("issue")
                active = updates["conversation"].get("active_issues", current_state.get("conversation", {}).get("active_issues", []))
                if issue and issue not in active:
                    updates["conversation"]["active_issues"] = active + [issue]
                    
            elif event_type == "ISSUE_RESOLVED":
                issue = event.get("issue")
                active = updates["conversation"].get("active_issues", current_state.get("conversation", {}).get("active_issues", []))
                resolved = updates["conversation"].get("resolved_issues", current_state.get("conversation", {}).get("resolved_issues", []))
                if issue and issue in active:
                    active.remove(issue)
                    updates["conversation"]["active_issues"] = active
                    if issue not in resolved:
                        updates["conversation"]["resolved_issues"] = resolved + [issue]
                        
            elif event_type == "INTENT_CHANGED":
                new_intent = event.get("intent")
                updates["conversation"]["previous_intent"] = current_state.get("conversation", {}).get("current_intent")
                updates["conversation"]["current_intent"] = new_intent
                
        # Escalation Logic (workflow.requires_human)
        # Default to False
        updates["workflow"]["requires_human"] = False
        
        # We need the current active issues to check for unresolved status
        active = updates.get("conversation", {}).get("active_issues", current_state.get("conversation", {}).get("active_issues", []))
        
        # Check active events for escalation triggers
        for event in events:
            event_type = event.get("event")
            
            # Rule 1: Customer explicitly requests a human agent
            if event_type == "ESCALATION_REQUESTED":
                updates["workflow"]["requires_human"] = True
                
            # Rule 2: Company policy requires manual handling
            elif event_type == "MANUAL_APPROVAL_REQUIRED":
                updates["workflow"]["requires_human"] = True
                
            # Rule 3: Customer is frustrated AND the issue is still unresolved
            elif event_type == "CUSTOMER_FRUSTRATED" and len(active) > 0:
                updates["workflow"]["requires_human"] = True
                
            # Rule 4: Repeated troubleshooting has failed
            elif event_type == "TROUBLESHOOTING_FAILED":
                updates["workflow"]["requires_human"] = True
                
            # Rule 5: A specialist explicitly recommends human escalation
            elif event_type == "SPECIALIST_ESCALATION_RECOMMENDED":
                updates["workflow"]["requires_human"] = True
                
        return updates
