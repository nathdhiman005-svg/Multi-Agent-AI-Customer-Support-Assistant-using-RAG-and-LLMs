class StateFormatter:
    def format(self, state_data: dict) -> str:
        """
        Formats the dialogue state dictionary into a readable string for the LLM.
        Acts as an intelligent serializer to avoid Schema Bias by omitting empty, null, or false fields.
        """
        output = []
        
        # Helper to format lists
        def format_list(title, items):
            if items and len(items) > 0:
                output.append(f"{title}:")
                for item in items:
                    output.append(f"- {item}")
                output.append("") # blank line

        # 1. Product
        product = state_data.get("entities", {}).get("current_product")
        if product:
            output.append("Current Product:")
            output.append(str(product))
            output.append("")
            
        # 2. Issues
        format_list("Active Issues", state_data.get("conversation", {}).get("active_issues", []))
        format_list("Resolved Issues", state_data.get("conversation", {}).get("resolved_issues", []))
        
        # 3. Customer Info
        sentiment = state_data.get("customer", {}).get("sentiment")
        if sentiment and sentiment != "Neutral":  # Neutral is default, omit unless they specifically want it? 
            # Wait, user said "Customer Sentiment: Frustrated". If Neutral, maybe omit? 
            # User instructions: "Do NOT output default values that carry no conversational meaning"
            # I will omit "Neutral".
            pass
        if sentiment and sentiment.lower() != "neutral":
            output.append("Customer Sentiment:")
            output.append(str(sentiment))
            output.append("")
            
        refund = state_data.get("customer", {}).get("refund_requested")
        if refund: # True
            output.append("Refund Requested:")
            output.append("Yes")
            output.append("")
            
        escalation = state_data.get("customer", {}).get("escalation_offered")
        if escalation: # True
            output.append("Escalation Offered:")
            output.append("Yes")
            output.append("")
            
        # 4. Entities
        order = state_data.get("entities", {}).get("order_id")
        if order:
            output.append("Order ID:")
            output.append(str(order))
            output.append("")
            
        payment = state_data.get("entities", {}).get("payment_method")
        if payment:
            output.append("Payment Method:")
            output.append(str(payment))
            output.append("")
            
        # Join lines
        final_str = "\n".join(output).strip()
        
        # If absolutely everything is empty, return a fallback so it's not totally blank
        if not final_str:
            return "No prior context."
            
        return final_str
