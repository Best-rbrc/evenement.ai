from typing import Dict, List, Any
from agents import Agent, Runner


async def coordinate_planning_session(coordinator: Agent, event_details: Dict[str, Any], required_agents: List[str], specialized_agents: Dict[str, Agent]) -> str:
    """Coordinate a planning session with all specialized agents."""
    
    # Create detailed planning prompt
    planning_prompt = f"""
    Please create a comprehensive event plan for "{event_details['event_name']}" by coordinating with the following specialized agents:
    
    Required Agents: {', '.join(required_agents)}
    
    For each agent, provide:
    1. Specific tasks and responsibilities
    2. Key deliverables and requirements
    3. Timeline and deadlines
    4. Budget considerations
    5. Dependencies and coordination needs
    6. Potential challenges and solutions
    
    Create an overall event timeline that shows:
    - Pre-event planning phases
    - Event day timeline
    - Post-event follow-up
    
    Ensure all aspects of the event are covered and that there are no conflicts or gaps in the planning.
    """
    
    try:
        result = await Runner.run_async(coordinator, planning_prompt)
        return result.final_output
    except Exception as e:
        return f"Error during coordination: {e}"

