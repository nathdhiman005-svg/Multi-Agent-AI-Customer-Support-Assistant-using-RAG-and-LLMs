from crewai import Crew, Process
from app.agents.support_agents import SupportAgents
from app.tasks.support_tasks import SupportTasks

class SupportCrew:
    def __init__(self):
        self.agents = SupportAgents()
        self.tasks = SupportTasks()

    def route_query(self, query: str) -> list[str]:
        """Use the Intent Router (Llama 3.2) to classify the query into one or multiple categories."""
        router = self.agents.intent_router_agent()
        routing_task = self.tasks.routing_task(router, query)
        
        crew = Crew(
            agents=[router],
            tasks=[routing_task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        raw_output = str(result.raw).strip()
        
        # Parse the comma-separated output
        valid_categories = ["Technical", "Billing", "Product", "Complaint", "FAQ"]
        found_categories = []
        for cat in valid_categories:
            if cat.lower() in raw_output.lower():
                found_categories.append(cat)
                
        if not found_categories:
            found_categories.append("FAQ") # Fallback
            
        return found_categories

    def process_query(self, query: str, categories: list[str]) -> str:
        """Execute the query dynamically assembling the required specialized agents."""
        active_agents = []
        active_tasks = []
        
        # 1. Dynamically add the specialized agents and their research tasks
        for category in categories:
            if category == "Technical":
                agent = self.agents.technical_support_agent()
                task = self.tasks.technical_task(agent, query)
            elif category == "Billing":
                agent = self.agents.billing_support_agent()
                task = self.tasks.billing_task(agent, query)
            elif category == "Product":
                agent = self.agents.product_support_agent()
                task = self.tasks.product_task(agent, query)
            elif category == "Complaint":
                agent = self.agents.complaint_support_agent()
                task = self.tasks.complaint_task(agent, query)
            else:
                agent = self.agents.general_faq_agent()
                task = self.tasks.faq_task(agent, query)
                
            active_agents.append(agent)
            active_tasks.append(task)
            
        # 2. Always add the Response Aggregator at the end
        aggregator_agent = self.agents.response_aggregator_agent()
        active_agents.append(aggregator_agent)
        
        aggregator_task = self.tasks.aggregator_task(aggregator_agent, query)
        active_tasks.append(aggregator_task)
        
        # 3. Execute the dynamically built Crew
        crew = Crew(
            agents=active_agents,
            tasks=active_tasks,
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result.raw
