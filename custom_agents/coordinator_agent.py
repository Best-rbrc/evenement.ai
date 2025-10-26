# workflows/coordinator_agent.py
from agents import Agent
from tools.analysis_tools import analyze_event_requirements, create_event_timeline, coordinate_agent_tasks
from typing import Dict, List, Any

def create_coordinator_agent(event_details: Dict[str, Any], required_agents: List[str], specialized_agents: Dict[str, Agent]) -> Agent:
    """Defines the Coordinator Agent that orchestrates planning."""
    handoffs = list(specialized_agents.values())

    system_prompt = f"""
You are the Event Planning Coordinator responsible for producing a structured, actionable event plan for
"{event_details['event_name']}", a {event_details['event_type']} event.

Your responsibilities:
- Assign portions of the budget to specialized agents (venue, catering, decor, etc.)
- Negotiate with them if they request more than allocated
- Answer their clarification questions
- Ensure that all agents coordinate smoothly and produce a unified plan
- Keep communication clear and focused on decisions

Agents will come to you for:
- Budget clarifications
- Interdependencies (e.g., catering depending on venue kitchen)
- Missing information

You can call agents again as needed to adjust or approve their proposals.

Always maintain a JSON log of:
- Current total budget
- Allocated budgets per agent
- Decisions made
- Pending clarifications

Your final output MUST be a single JSON object with the following fields:
{{
  "event_summary": "...",
  "venues": [...],
  "catering": [...],
  "speakers": [...],
  "budget_summary": {{...}},
  "communications": {{ "invitation": ..., "reminder": ..., "thank_you": ... }},
  "registration_form": {{...}},
  "vendor_checklist": [...],
  "risk_assessment": {{...}}
}}

Do not ask follow-up questions or request clarification. 
If information is missing, make reasonable assumptions and note them in a field named "assumptions".
Never end with a question. Output must be valid JSON, ready to parse.
"""

    return Agent(
        name="Event Planning Coordinator",
        instructions=system_prompt,
        tools=[analyze_event_requirements, create_event_timeline, coordinate_agent_tasks],
        handoffs=handoffs,
    )
