from crewai import Agent
from app.config.llm_config import get_ollama_llm
from app.tools.rag_tool import RAGSearchTool
from app.tools.email_tool import EscalationEmailTool

class SupportAgents:
    def __init__(self):
        # APIs (None, running 100% locally now)
        
        # Local Models
        self.qwen_3b = get_ollama_llm(model_name="qwen2.5:3b")
        self.llama_3b = get_ollama_llm(model_name="llama3.2:3b")
        self.phi4_mini = get_ollama_llm(model_name="phi4-mini")
        self.gemma_4b = get_ollama_llm(model_name="gemma3:4b")
        self.mistral_7b = get_ollama_llm(model_name="mistral")
        self.qwen_7b = get_ollama_llm(model_name="qwen2.5:7b")
        
        # The tool that gives agents access to ChromaDB
        self.rag_tool = RAGSearchTool()

    def intent_router_agent(self):
        return Agent(
            role='Customer Intent Classifier',
            goal='Accurately classify the customer query into one of the support departments: Technical, Billing, or FAQ.',
            backstory='You are a highly efficient dispatch agent. You read customer queries and immediately know which specialized department should handle it. You do not solve problems, you only route them.',
            verbose=True,
            allow_delegation=False,
            llm=self.llama_3b # Fast routing via local Llama 3.2 3B
        )

    def technical_support_agent(self, email_tool: EscalationEmailTool):
        return Agent(
            role='Senior Technical Support Specialist',
            goal='Solve customer technical issues by searching the knowledge base for manuals and troubleshooting steps.',
            backstory='You are an expert technician for NovaCart Electronics. You are patient, highly analytical, and always rely on official manuals to guide customers step-by-step through their technical problems.',
            verbose=True,
            allow_delegation=False,
            tools=[self.rag_tool, email_tool],
            llm=self.qwen_7b # Deep reasoning and RAG via local Qwen 2.5 7B
        )

    def billing_support_agent(self, email_tool: EscalationEmailTool):
        return Agent(
            role='Billing and Returns Specialist',
            goal='Help customers with refunds, warranties, pricing, and shipping policies by consulting the knowledge base.',
            backstory='You are a polite and detail-oriented billing agent for NovaCart Electronics. You handle sensitive refund and payment questions by strictly following the official company policies.',
            verbose=True,
            allow_delegation=False,
            tools=[self.rag_tool, email_tool],
            llm=self.qwen_3b # Strict adherence to rules via Qwen 3B
        )

    def general_faq_agent(self, email_tool: EscalationEmailTool):
        return Agent(
            role='Customer Service Representative',
            goal='Answer general questions about the company, products, and generic FAQs.',
            backstory='You are the friendly face of NovaCart Electronics. You answer general product inquiries and basic FAQs.',
            verbose=True,
            allow_delegation=False,
            tools=[self.rag_tool, email_tool],
            llm=self.phi4_mini # Long context for large policies via Phi4-mini
        )

    def product_support_agent(self, email_tool: EscalationEmailTool):
        return Agent(
            role='Product Specialist',
            goal='Provide detailed information, specifications, and comparisons for NovaCart Electronics products.',
            backstory='You are an enthusiastic product expert. You help customers choose the right electronics by consulting the product catalog and providing tailored recommendations.',
            verbose=True,
            allow_delegation=False,
            tools=[self.rag_tool, email_tool],
            llm=self.llama_3b # Stable catalog queries via Llama 3.2 3B
        )

    def complaint_support_agent(self, email_tool: EscalationEmailTool):
        return Agent(
            role='Customer Escalation & Complaint Specialist',
            goal='De-escalate angry customers, apologize for inconveniences, and offer resolutions based on company policy.',
            backstory='You are a highly empathetic and calm escalation manager. You handle complaints and negative feedback with grace, always aiming to retain the customer and resolve their issue fairly.',
            verbose=True,
            allow_delegation=False,
            tools=[self.rag_tool, email_tool],
            llm=self.qwen_7b # Empathetic and conversational via local Qwen 2.5 7B
        )

    def response_aggregator_agent(self):
        return Agent(
            role='Lead Communications Manager',
            goal='Take raw technical or billing solutions and format them into a beautiful, consistent, and highly polite customer response.',
            backstory='You are the final voice of NovaCart Electronics. You never search for answers yourself; you take the raw notes provided by your specialized agents and rewrite them to ensure perfect grammar, empathetic tone, and professional formatting before sending them to the customer.',
            verbose=True,
            allow_delegation=False,
            llm=self.mistral_7b # Beautiful formatting and logic via local Mistral 7B
        )
