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
from agents import Agent, AgentOutputSchema
from typing import Dict, List, Any
from workflows.pydantic_schemas import PlanningOutput, FinalPlanOutput


def create_planning_coordinator(event_details: Dict[str, Any], required_agents: List[str]) -> Agent:
    """Create coordinator for Phase 1: Planning and agent selection.
    
    Uses structured outputs to ensure valid JSON responses.
    
    Args:
        event_details: Dictionary with event information
        required_agents: List of available agent types
        
    Returns:
        Agent configured for planning phase with PlanningOutput schema
    """
    system_prompt = f"""You are the Event Planning Coordinator analyzing requirements for "{event_details['event_name']}", a {event_details['event_type']} event.

YOUR TASK: Analyze the event requirements and determine which specialist agents to use and in what order.

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

DECISION GUIDELINES:
1. ALWAYS include budgeting early (after venue/catering for cost estimates)
2. Include scheduling for multi-session events with speakers
3. Consider event type when selecting specialists
4. Order matters - dependencies should be considered

OUTPUT: You will return a structured JSON with:
- analysis: Your analysis of the event requirements
- required_agents: List of agent names to use (from available list)
- execution_order_rationale: Why this order makes sense
- special_considerations: Any special notes or constraints"""

    return Agent(
        name="Planning Coordinator",
         output_type=AgentOutputSchema(PlanningOutput, strict_json_schema=False),
        instructions=system_prompt,
    )


def create_finalization_coordinator(event_details: Dict[str, Any], required_agents: List[str], specialist_outputs: Dict[str, Any]) -> Agent:
    """Create coordinator for Phase 3: Final plan synthesis.
    
    Uses structured outputs to ensure valid JSON responses.
    
    Args:
        event_details: Dictionary with event information
        required_agents: List of agents that were used
        specialist_outputs: Outputs from all specialist agents
        
    Returns:
        Agent configured for finalization with FinalPlanOutput schema
    """
    outputs_summary = "\n".join([
        f"- {name}: {len(str(output))} chars of data"
        for name, output in specialist_outputs.items()
    ])
    
    system_prompt = f"""You are the Event Planning Coordinator synthesizing the final plan for "{event_details['event_name']}".

EVENT CONTEXT:
- Event: {event_details.get('event_name', 'N/A')}
- Type: {event_details.get('event_type', 'N/A')}
- Date: {event_details.get('event_date', 'TBD')}
- Location: {event_details.get('location_preference', 'Flexible')}
- Budget: {event_details.get('budget_range', 'Not specified')}
- Guests: {event_details.get('guest_count', 'TBD')}

SPECIALIST OUTPUTS RECEIVED:
{outputs_summary}

YOUR TASK: Create a comprehensive final event plan by synthesizing all specialist outputs.

CRITICAL REQUIREMENTS:
1. Include COMPLETE specialist outputs in "recommendations" field - not summaries
2. Create a detailed timeline with phases, tasks, and deadlines
3. Build a schedule with sessions (use scheduling agent output if available)
4. Synthesize budget from budgeting agent output
5. Identify risks and mitigation strategies
6. Create actionable action items with owners and deadlines
7. Document all assumptions made

The output MUST follow the FinalPlanOutput schema exactly:
- executive_summary: 2-3 paragraph overview
- timeline: List of phases with tasks and deadlines
- schedule: Sessions with times, rooms, speakers (mark as basic if not optimized)
- budget: Total, allocated, by category, status
- recommendations: COMPLETE specialist outputs (not empty)
- risks: Identified risks with severity and mitigation
- action_items: Actionable items with priority and deadline
- assumptions: All assumptions made during planning"""

    return Agent(
        name="Finalization Coordinator",
         output_type=AgentOutputSchema(FinalPlanOutput, strict_json_schema=False),
        instructions=system_prompt,
    )


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
3. Schedule Optimization: Use Scheduling Agent for complex multi-session events with constraint optimization
4. Quality Control: Review specialist outputs for gaps, conflicts, or budget issues
5. Synthesis: Produce comprehensive, actionable final plans

BUDGETING WORKFLOW (CRITICAL):
- ALWAYS include "budgeting" as one of the first specialists (after initial needs assessment)
- BEFORE other specialists provide costs: Have Budgeting Agent create baseline allocation
- AFTER specialists provide estimates: Have Budgeting Agent validate costs and run what-if scenarios
- IF budget conflicts arise: Immediately handoff to Budgeting Agent for scenario analysis
- IN final plan: Include Budgeting Agent's itemized breakdown and scenario comparisons

SCHEDULING WORKFLOW (FOR MULTI-SESSION EVENTS):
- USE Scheduling Agent when: conferences, workshops, multi-track events with speakers/rooms
- AFTER Programme & Speakers agents provide session details
- Scheduling Agent will: optimize timeslots, resolve conflicts, maximize room utilization
- IN final plan: Include optimized schedule with metrics (duration, utilization, conflicts resolved)

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
  "timeline": [{{"phase": "Phase name (e.g., 'Pre-Event Planning', 'Event Execution', 'Post-Event')", "tasks": ["Task 1", "Task 2", ...], "deadline": "YYYY-MM-DD"}}],
  "schedule": {{
    "optimized": true/false,  // true if scheduling agent was used, false otherwise
    "sessions": [...],  // REQUIRED - ALWAYS include at least one session. For multi-day events, include "date": "YYYY-MM-DD" for each session
    "metrics": {{  // Optional if scheduling agent was not used
      "total_duration": "...",
      "room_utilization": {{}},
      "conflicts_resolved": "..."
    }},
    "status": "optimal | feasible | infeasible | basic"  // "basic" if created from event details
  }},
  "budget": {{
    "total_available": "...",
    "total_allocated": "...",
    "by_category": {{}},
    "status": "within_budget | over_budget | at_limit"
  }},
  "recommendations": {{"venue": {{...}}, "catering": {{...}}, ...}},  // MUST include COMPLETE specialist outputs, not empty objects
  "risks": [{{"risk": "...", "severity": "...", "mitigation": "..."}}],
  "action_items": [{{"action": "...", "owner": "...", "deadline": "...", "priority": "..."}}],
  "assumptions": [...]
}}"""

    return Agent(
        name="Event Planning Coordinator",
        instructions=system_prompt,
        handoffs=handoffs,
    )
