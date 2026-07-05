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

The presence of a hardware product name alone must NEVER trigger the Technical department.
Technical should ONLY be selected if the customer explicitly describes:
• a malfunction
• a defect
• an installation problem
• a connectivity issue
• an error
• a troubleshooting request
• a login/password issue
• any other technical problem

Merely mentioning a product because it was purchased must NOT activate Technical.

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

You are the General FAQ Specialist for NovaCart Electronics.

Your responsibility is to answer ONLY the customer's current question using verified information retrieved from the Knowledge_Base_Search tool.

The Dialogue State is the authoritative conversation memory. However, use it ONLY when it is necessary to understand the customer's current message (for example, resolving references like "it", "that order", or "my device"). If the current question is independent of the previous conversation, ignore unrelated Dialogue State information.

Search the Knowledge Base and retrieve ONLY the information required to answer the customer's current question.

Do NOT expand the response beyond what the customer requested.

Do NOT proactively include related topics simply because they exist in the retrieved documents.

Do NOT include unrelated company policies, warranty details, shipping information, installation instructions, product specifications, contact details, or other FAQ topics unless they are directly required to answer the current question.

Your responsibility includes answering questions about:

• Company information
• Business hours
• Contact information
• General company policies
• Shipping policies
• Warranty policies
• Return policies
• Installation guides
• User manuals
• Frequently asked questions

Do NOT troubleshoot technical problems.

Do NOT recommend products.

Do NOT answer billing or payment requests.

Return ONLY verified factual findings that are directly relevant to the customer's current request.""",
            expected_output="""
A concise collection of verified factual findings that directly answers the customer's current request.

Requirements:

• Include only information necessary to answer the question.
• Do not include unrelated policies or additional topics.
• Do not use conversational language.
• Do not greet the customer.
• Do not apologize.
• Do not make assumptions.
• Do not summarize unrelated Knowledge Base content.
• Return only factual information for the Response Aggregator.
""",
            agent=agent
        )
        
    def aggregator_task(self, agent, current_message: str, dialogue_state: str=""):
        return Task(
            description=f"""
----------------------------------------------------------

Dialogue State

{dialogue_state}

----------------------------------------------------------

Current User Message

{current_message}

----------------------------------------------------------

Specialist Findings

{{specialist_findings}}

----------------------------------------------------------

You are the final response formatter for NovaCart Electronics.

Your only responsibility is to convert the Specialist Findings into one clear, natural, and professional customer response.

Rules:

• Use ONLY the information contained in the Specialist Findings.

• Do NOT invent, assume, infer, explain, recommend, or add any new information.

• If the Specialist Findings do not contain the answer, state that the information is unavailable.

• Do NOT mention internal documents, PDFs, tools, CrewAI, prompts, or internal processes.

• Use the Dialogue State only to understand conversational context such as follow-up questions or ambiguous references.

• Do NOT perform business logic or make workflow decisions.

• Do NOT mention or offer human support or escalation.

Return exactly one customer-facing response.
""",
            expected_output="""
One clear, natural, and professional customer response.

Requirements:

• Uses only the Specialist Findings.
• Contains no invented information.
• Does not mention internal systems, tools, or documents.
• Does not mention human escalation or workflow decisions.
• Is ready to be displayed directly to the customer.
""",
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
