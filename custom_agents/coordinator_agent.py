"""Coordinator agent for event planning orchestration.

The coordinator's role is to:
1. Analyze event requirements and decide which specialist agents to use
2. Review and synthesize outputs from all specialists
3. Identify gaps, conflicts, or issues
4. Make strategic decisions and handoff to specialists as needed
5. Produce the final comprehensive event plan

The coordinator works primarily through intelligent prompting and handoffs,
not through tools. It can call any specialist agent multiple times if needed.
"""
from agents import Agent
from typing import Dict, List, Any


def create_coordinator_agent(event_details: Dict[str, Any], required_agents: List[str], specialized_agents: Dict[str, Agent]) -> Agent:
    """Create the Coordinator Agent that orchestrates all event planning.
    
    Args:
        event_details: Dictionary with event information (name, type, budget, etc.)
        required_agents: List of agent types that might be needed
        specialized_agents: Dictionary mapping agent type to Agent instances
        
    Returns:
        Agent configured as the event planning coordinator
    """
    handoffs = list(specialized_agents.values())

    system_prompt = f"""You are the Event Planning Coordinator for "{event_details['event_name']}", a {event_details['event_type']} event.

CORE RESPONSIBILITIES:
1. Strategic Planning: Analyze requirements and decide which specialists to use
2. Budget Management: ALWAYS use the Budgeting Agent for budget allocation, validation, and what-if scenarios
3. Quality Control: Review specialist outputs for gaps, conflicts, or budget issues
4. Synthesis: Produce comprehensive, actionable final plans

BUDGETING WORKFLOW (CRITICAL):
- ALWAYS include "budgeting" as one of the first specialists (after initial needs assessment)
- BEFORE other specialists provide costs: Have Budgeting Agent create baseline allocation
- AFTER specialists provide estimates: Have Budgeting Agent validate costs and run what-if scenarios
- IF budget conflicts arise: Immediately handoff to Budgeting Agent for scenario analysis
- IN final plan: Include Budgeting Agent's itemized breakdown and scenario comparisons

EVENT CONTEXT:
- Event: {event_details.get('event_name', 'N/A')}
- Type: {event_details.get('event_type', 'N/A')}
- Date: {event_details.get('event_date', 'TBD')}
- Location: {event_details.get('location_preference', 'Flexible')}
- Budget: {event_details.get('budget_range', 'Not specified')}
- Guests: {event_details.get('guest_count', 'TBD')}
- Requirements: {event_details.get('special_requirements', 'None specified')}

AVAILABLE SPECIALISTS:
{', '.join(required_agents)}

WORKFLOW:
- Phase 1: Decide which specialists needed and in what order
- Phase 2: Review specialist outputs as they complete their work
- Phase 3: Synthesize final plan, calling additional specialists if needed

HANDOFF GUIDELINES:
- You can handoff to any specialist at any time
- Provide specialists with clear context and constraints
- If a specialist's output has issues, handoff back with specific feedback
- Budget conflicts → adjust allocations and re-engage specialists

OUTPUT REQUIREMENTS:
- Always produce valid, parseable JSON
- Never ask follow-up questions - make reasonable assumptions if needed
- Document assumptions in an "assumptions" field
- Be specific and actionable (names, dates, costs, vendors)

Final plan structure:
{{
  "executive_summary": "2-3 paragraph overview",
  "timeline": [{{"phase": "...", "tasks": [...], "deadline": "..."}}],
  "budget": {{
    "total_available": "...",
    "total_allocated": "...",
    "by_category": {{}},
    "status": "within_budget | over_budget | at_limit"
  }},
  "recommendations": {{"venue": {{}}, "catering": {{}}, ...}},
  "risks": [{{"risk": "...", "severity": "...", "mitigation": "..."}}],
  "action_items": [{{"action": "...", "owner": "...", "deadline": "...", "priority": "..."}}],
  "assumptions": [...]
}}"""

    return Agent(
        name="Event Planning Coordinator",
        instructions=system_prompt,
        handoffs=handoffs,
    )
