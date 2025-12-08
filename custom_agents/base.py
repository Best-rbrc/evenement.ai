"""Specialized agents for different aspects of event planning."""
from typing import Dict, List
from agents import Agent

# Import agent factories directly from their modules to avoid circular import
from custom_agents.venue_agent import create_venue_agent
from custom_agents.catering_agent import create_catering_agent
from custom_agents.speaker_agent import create_speakers_agent
from custom_agents.programme_agent import create_programme_agent
from custom_agents.communication_agent import create_communication_agent
from custom_agents.activities_agent import create_activities_agent
from custom_agents.entertainment_agent import create_entertainment_agent
from custom_agents.calendar_agent import create_calendar_agent
from custom_agents.form_agent import create_form_agent
from custom_agents.budgeting_agent import create_budgeting_agent
from custom_agents.scheduling_agent import create_scheduling_agent
from custom_agents.logo_agent import create_logo_agent


# Agent creation mapping
AGENT_CREATORS = {
    "venue": create_venue_agent,
    "catering": create_catering_agent,
    "speakers": create_speakers_agent,
    "programme": create_programme_agent,
    "communication": create_communication_agent,
    "activities": create_activities_agent,
    "entertainment": create_entertainment_agent,
    "budgeting": create_budgeting_agent,
    "calendar": create_calendar_agent,
    "form": create_form_agent,
    "scheduling": create_scheduling_agent,
    "logo": create_logo_agent,
}



def create_specialized_agents(required_agents: List[str], mcp_servers=None) -> Dict[str, Agent]:
    """Create specialized agents based on the required agent types.
    
    Args:
        required_agents: List of agent type names to create
        mcp_servers: Optional MCPServers instance to pass to agents that handle external data:
                    - calendar: sandboxed calendar file writing
                    - form: sandboxed form data handling from external sources
    """
    agents = {}
    
    for agent_type in required_agents:
        if agent_type in AGENT_CREATORS:
            creator = AGENT_CREATORS[agent_type]
            # Pass mcp_servers to agents that handle external/user input data
            if agent_type in ("calendar", "form") and mcp_servers is not None:
                agents[agent_type] = creator(mcp_servers=mcp_servers)
            else:
                agents[agent_type] = creator()
        else:
            # Create a generic agent for unknown types
            agents[agent_type] = Agent(
                name=f"{agent_type.title()} Specialist",
                instructions=f"You are a specialist in {agent_type} planning and coordination."
            )
    
    return agents
