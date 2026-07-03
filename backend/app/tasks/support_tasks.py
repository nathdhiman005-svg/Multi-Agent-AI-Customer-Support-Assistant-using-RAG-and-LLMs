from crewai import Task

class SupportTasks:
    
    def routing_task(self, agent, query: str):
        return Task(
            description=f"Analyze this customer query: '{query}'. Classify it into one OR MORE of these categories: 'Technical', 'Billing', 'Product', 'Complaint', or 'FAQ'. If the query spans multiple domains (e.g. payment issue AND a bug), output all applicable categories as a comma-separated list. Output ONLY the category names.",
            expected_output="A comma-separated list of categories: e.g., Technical, Billing",
            agent=agent
        )

    def billing_task(self, agent, query: str, user_email: str = ""):
        return Task(
            description=f"A customer (email: {user_email}) has submitted a query: '{query}'. As the Billing Specialist, you handle Payment issues, Subscriptions, Invoices, and Refunds. Use your Knowledge_Base_Search tool to find relevant information regarding these aspects. Provide the raw facts, policies, and steps needed to solve your part of the problem. If other agents have already provided info, append your findings to theirs.",
            expected_output="Detailed raw facts and step-by-step solutions extracted from the knowledge base regarding billing and payments. Do not worry about pleasantries.",
            agent=agent
        )

    def technical_task(self, agent, query: str, user_email: str = ""):
        return Task(
            description=f"A customer (email: {user_email}) has submitted a query: '{query}'. As the Technical Support Specialist, you handle Logins, Password resets, Installations, Errors, and Bugs. Use your Knowledge_Base_Search tool to find relevant troubleshooting steps regarding these aspects. Provide the raw facts, policies, and steps needed to solve your part of the problem. If other agents have already provided info, append your findings to theirs.",
            expected_output="Detailed raw facts and step-by-step technical solutions extracted from the knowledge base regarding technical issues. Do not worry about pleasantries.",
            agent=agent
        )

    def product_task(self, agent, query: str, user_email: str = ""):
        return Task(
            description=f"A customer (email: {user_email}) has submitted a query: '{query}'. As the Product Specialist, you handle Features, Pricing, Comparisons, and Availability. Use your Knowledge_Base_Search tool to find relevant product information regarding these aspects. Provide the raw facts and policies needed to solve your part of the problem. If other agents have already provided info, append your findings to theirs.",
            expected_output="Detailed raw facts extracted from the knowledge base regarding product features, pricing, or availability. Do not worry about pleasantries.",
            agent=agent
        )

    def complaint_task(self, agent, query: str, user_email: str = ""):
        return Task(
            description=f"A customer (email: {user_email}) has submitted a query: '{query}'. As the Complaint Specialist, you handle Complaints, Escalations, and Customer dissatisfaction. Review the knowledge base for escalation policies or appropriate compensation steps if applicable. Provide the raw guidelines on how to handle this specific escalation. If other agents have already provided info, append your findings to theirs.",
            expected_output="Raw guidelines and policies extracted from the knowledge base regarding escalations and complaints. Do not worry about pleasantries.",
            agent=agent
        )

    def faq_task(self, agent, query: str, user_email: str = ""):
        return Task(
            description=f"A customer (email: {user_email}) has submitted a query: '{query}'. As the FAQ Specialist, you handle Company policies, General questions, and Contact information. Use your Knowledge_Base_Search tool to find relevant information regarding these aspects. Provide the raw facts needed to solve your part of the problem. If other agents have already provided info, append your findings to theirs.",
            expected_output="Detailed raw facts extracted from the knowledge base regarding general FAQs. Do not worry about pleasantries.",
            agent=agent
        )
        
    def aggregator_task(self, agent, query: str):
        return Task(
            description=f"Review the combined raw solutions provided by the specialized agents regarding this customer query: '{query}'. Rewrite everything into a single, cohesive, polished response for the customer. Ensure the tone is empathetic and conversational. CRITICAL RULE 1: Never mention 'knowledge base' or cite '.pdf' files. Act as a human expert. CRITICAL RULE 2: You are writing a single instant message chat bubble. End your response immediately after your final sentence. Do not include any signatures, names, or sign-offs at the end. CRITICAL RULE 3: If the issue seems unresolvable, complex, or you couldn't find a complete solution, you MUST append this exact message at the end of your response: 'If these steps are not resolving your issue, you can escalate this issue to get human support. Do you want to escalate? [Type yes to escalate]'",
            expected_output="A polished, polite, and final response ready to be sent directly to the customer's live chat window, optionally ending with the 'Type yes to escalate' prompt. Must be purely conversational text. Stop generating immediately after the final sentence.",
            agent=agent
        )

    def email_task(self, agent, customer_email: str, summary: str):
        return Task(
            description=f"You are the Automated Dispatch Agent. An issue needs to be escalated to the admin for the customer: {customer_email}. The summary is: {summary}. You MUST use your EscalationEmailTool right now. This tool will automatically send a detailed summary to the human admin team AND a confirmation receipt to the customer's email. Pass customer_email='{customer_email}' and issue_summary='{summary}' to the tool.",
            expected_output="A confirmation string that the EscalationEmailTool was executed successfully.",
            agent=agent
        )
