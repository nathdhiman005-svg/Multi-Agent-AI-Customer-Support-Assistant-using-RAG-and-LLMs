from crewai import Crew, Process
from app.agents.support_agents import SupportAgents
from app.tasks.support_tasks import SupportTasks
import os

os.environ["OTEL_SDK_DISABLED"] = "true"

def test_aggregator(scenario_name, dialogue_state, current_message, specialist_findings):
    agents = SupportAgents()
    tasks = SupportTasks()
    
    agent = agents.response_aggregator_agent()
    task = tasks.aggregator_task(agent, current_message, dialogue_state)
    
    # Manually inject findings to simulate the output of previous tasks
    task.context = []  # No context tasks
    # We must patch the description because CrewAI only interpolates {specialist_findings} from previous tasks
    # Since we are running it standalone, we will replace it manually just for this test
    task.description = task.description.replace("{specialist_findings}", specialist_findings)
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False
    )
    
    print(f"\n======================================")
    print(f"SCENARIO: {scenario_name}")
    print(f"======================================")
    result = crew.kickoff()
    print(f"[Aggregator Response]:\n{result.raw}")
    return result.raw

# 1. Technical returns findings, Billing returns nothing
test_aggregator(
    "Technical returns findings, Billing returns nothing",
    "Current Product: NovaBook Pro",
    "My laptop screen is flickering and I want a refund.",
    "Technical Findings: The screen flickering is a known driver issue. Recommend updating graphics driver.\nBilling Findings: [NO FINDINGS]"
)

# 2. Billing returns findings, Technical returns nothing
test_aggregator(
    "Billing returns findings, Technical returns nothing",
    "Current Product: NovaPhone X\nRefund Requested: Yes",
    "I want a refund for my phone, the battery is completely dead.",
    "Technical Findings: [NO FINDINGS]\nBilling Findings: Returns are accepted within 30 days of purchase for a full refund."
)

# 3. Every specialist returns empty findings
test_aggregator(
    "Every specialist returns empty findings",
    "Current Product: NovaVR Headset",
    "How do I enter the matrix?",
    "Specialist Findings: [NO FINDINGS]"
)

# 4. One specialist intentionally returns incomplete findings
test_aggregator(
    "One specialist intentionally returns incomplete findings",
    "Current Product: SmartHome Hub",
    "How do I reset my hub and what is the warranty?",
    "Technical Findings: To reset the hub, hold the power button for 10 seconds.\nBilling Findings: Warranty information could not be found."
)
