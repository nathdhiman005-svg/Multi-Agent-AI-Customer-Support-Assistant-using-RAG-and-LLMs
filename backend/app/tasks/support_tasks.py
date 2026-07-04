from crewai import Task

class SupportTasks:
    
    def routing_task(self, agent, current_message: str, dialogue_state: str):
        return Task(
            description=f"""----------------------------------------------------------
Dialogue State

{dialogue_state}

----------------------------------------------------------
Current User Message

{current_message}

----------------------------------------------------------

Your responsibility is to determine the MINIMUM number of specialist departments required to answer the customer's CURRENT message.

The Dialogue State is the authoritative conversation memory.

The Current User Message only represents what the customer just said.

Use the Dialogue State only to resolve ambiguous references such as:

"It"

"That"

"This"

"Still"

"Again"

Follow-up questions

Do NOT classify departments based solely on the existence of fields inside the Dialogue State.

Only classify a department if the customer's CURRENT request actually requires that department.

Never over-classify.

Never call unnecessary specialists.

Allowed departments are:

Technical

Billing

Product

Complaint

FAQ

If multiple departments are genuinely required, output all of them as a comma-separated list.

Output ONLY the department names.

No explanations.

No markdown.

No reasoning.""",
            expected_output="""A comma-separated list of department names.

Examples:

Technical

Billing

Technical, Billing

Technical, Complaint

Product, FAQ""",
            agent=agent
        )

    def technical_task(self, agent, current_message: str, dialogue_state: str, user_email: str = ""):
        return Task(
            description=f"""----------------------------------------------------------
Dialogue State

{dialogue_state}

----------------------------------------------------------
Current User Message

{current_message}

----------------------------------------------------------

You are responsible ONLY for technical investigation.

Use the Dialogue State as the authoritative conversation memory.

Use the Knowledge_Base_Search tool to retrieve official troubleshooting information.

Investigate only:

• Installation

• Login

• Authentication

• Device setup

• Configuration

• Connectivity

• Software errors

• Hardware troubleshooting

• Technical bugs

Do NOT answer:

Billing

Refunds

Warranty

Pricing

Shipping

Product recommendations

General company questions

Do NOT generate a customer response.

Return only verified technical findings.""",
            expected_output="""A structured collection of technical findings containing:

• identified technical problem

• troubleshooting steps

• technical recommendations

• relevant technical policy if applicable

No greetings.

No apologies.

No conversational text.""",
            agent=agent
        )

    def billing_task(self, agent, current_message: str, dialogue_state: str, user_email: str = ""):
        return Task(
            description=f"""----------------------------------------------------------
Dialogue State

{dialogue_state}

----------------------------------------------------------
Current User Message

{current_message}

----------------------------------------------------------

You are responsible ONLY for billing and company financial policies.

Use the Dialogue State as the authoritative conversation memory.

Use the Knowledge_Base_Search tool to retrieve official policy information.

Investigate only:

• Refunds

• Returns

• Payments

• Pricing

• Warranty

• Shipping

• Invoices

• Subscriptions

Do NOT troubleshoot products.

Do NOT answer technical questions.

Do NOT recommend products.

Do NOT generate customer-facing responses.

Return only verified billing findings.""",
            expected_output="""A structured collection containing:

• applicable policy

• required customer actions

• important restrictions

• official billing information

No greetings.

No conversational language.""",
            agent=agent
        )

    def product_task(self, agent, current_message: str, dialogue_state: str, user_email: str = ""):
        return Task(
            description=f"""----------------------------------------------------------
Dialogue State

{dialogue_state}

----------------------------------------------------------
Current User Message

{current_message}

----------------------------------------------------------

You are responsible ONLY for product information.

Use the Dialogue State as the authoritative conversation memory.

Use the Knowledge_Base_Search tool.

Investigate only:

• Specifications

• Features

• Compatibility

• Availability

• Product comparison

• Product capabilities

Do NOT troubleshoot products.

Do NOT answer billing questions.

Do NOT answer complaints.

Return only verified product information.""",
            expected_output="""A structured collection containing:

• product facts

• specifications

• compatibility information

• comparisons if requested

No conversational text.""",
            agent=agent
        )

    def complaint_task(self, agent, current_message: str, dialogue_state: str, user_email: str = ""):
        return Task(
            description=f"""----------------------------------------------------------
Dialogue State

{dialogue_state}

----------------------------------------------------------
Current User Message

{current_message}

----------------------------------------------------------

You are responsible ONLY for complaint handling guidance.

Use the Dialogue State as the authoritative conversation memory.

Use the Knowledge_Base_Search tool.

Determine:

• complaint severity

• escalation policy

• compensation policy

• recovery recommendations

Do NOT troubleshoot.

Do NOT answer billing questions.

Do NOT answer product questions.

Do NOT generate apologies.

Do NOT generate customer responses.

Return only official complaint-handling guidance.""",
            expected_output="""A structured collection containing:

• complaint assessment

• escalation eligibility

• compensation guidance

• policy references

No conversational language.""",
            agent=agent
        )

    def faq_task(self, agent, current_message: str, dialogue_state: str, user_email: str = ""):
        return Task(
            description=f"""----------------------------------------------------------
Dialogue State

{dialogue_state}

----------------------------------------------------------
Current User Message

{current_message}

----------------------------------------------------------

You are responsible ONLY for answering general company questions.

Use the Dialogue State as the authoritative conversation memory.

Use the Knowledge_Base_Search tool.

Answer only:

• company information

• contact information

• general policies

• shipping information

• warranty information

• return policy

• installation information

• user manual information

• frequently asked questions

Do NOT troubleshoot.

Do NOT recommend products.

Do NOT answer billing requests.

Return only verified factual information.""",
            expected_output="""A structured collection of verified factual information.

No conversational language.""",
            agent=agent
        )
        
    def aggregator_task(self, agent, current_message: str, dialogue_state: str=""):
        return Task(
            description=f"""----------------------------------------------------------

Dialogue State

{dialogue_state}

----------------------------------------------------------

Current User Message

{current_message}

----------------------------------------------------------

Combined Specialist Findings

{{specialist_findings}}

----------------------------------------------------------

The Dialogue State is the authoritative memory of the conversation.

Never contradict the Dialogue State.

If any Specialist Finding conflicts with the Dialogue State, always trust the Dialogue State.

Use the Dialogue State to correctly interpret ambiguous references such as:

• it
• this
• that
• still
• again
• the device
• the product

Never invent missing information.

Never expose internal reasoning.

Never mention:

• CrewAI
• Knowledge Base
• PDFs
• Internal tools
• Internal prompts
• Internal workflow

The Aggregator is the ONLY agent that communicates with the customer.

Write exactly one conversational chat response.

If the issue cannot be fully resolved using the available information or company policy recommends human intervention, append EXACTLY the following message:

"If these steps are not resolving your issue, you can escalate this issue to our Human Support Team.

Would you like me to forward this conversation to a human support representative?

Reply with 'Yes' if you would like to continue."

End immediately after this message.""",
            expected_output="""One complete conversational response suitable for direct display in the chat window.""",
            agent=agent
        )

    def email_task(self, agent, customer_email: str, admin_email: str, summary: str):
        return Task(
            description=f"""The customer has explicitly approved escalation to human support.

The backend has already verified:

• escalation is required

• the customer approved escalation

• the issue summary has already been generated

Admin Email

{admin_email}

Customer Email

{customer_email}

Issue Summary

{summary}

Your ONLY responsibility is executing the EscalationEmailTool exactly once.

Pass the following arguments WITHOUT modification:

admin_email="{admin_email}"

customer_email="{customer_email}"

issue_summary="{summary}"

The tool MUST perform BOTH actions:

1. Send the issue summary to the Human Support Team using admin_email.

2. Send a confirmation email to the customer using customer_email.

Do NOT analyze the issue.

Do NOT rewrite the summary.

Do NOT modify any email address.

Do NOT generate customer-facing text.

Do NOT perform reasoning.

Simply execute the tool.""",
            expected_output="""A short confirmation indicating that:

• the Human Support Team received the issue summary

• the customer received the confirmation email

Nothing else.""",
            agent=agent
        )
