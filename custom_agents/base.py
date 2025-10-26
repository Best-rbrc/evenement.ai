"""Specialized agents for different aspects of event planning."""
from typing import Dict, List
from agents import Agent, function_tool, WebSearchTool
from config import AGENT_SPECIALIZATIONS
from custom_agents import create_venue_agent, create_catering_agent, create_speakers_agent, \
    create_programme_agent, create_communication_agent, create_decoration_agent, \
    create_photography_agent, create_music_agent, create_entertainment_agent, \
    create_registration_agent, create_sponsors_agent, create_seating_agent, \
    create_materials_agent, create_networking_agent, create_media_agent, \
    create_demo_agent, create_fundraising_agent, create_activities_agent, \
    create_accommodation_agent

# Agent creation mapping
AGENT_CREATORS = {
    "venue": create_venue_agent,
    "catering": create_catering_agent,
    "speakers": create_speakers_agent,
    "programme": create_programme_agent,
    "communication": create_communication_agent,
    "decoration": create_decoration_agent,
    "photography": create_photography_agent,
    "music": create_music_agent,
    "entertainment": create_entertainment_agent,
    "registration": create_registration_agent,
    "sponsors": create_sponsors_agent,
    "seating": create_seating_agent,
    "materials": create_materials_agent,
    "networking": create_networking_agent,
    "media": create_media_agent,
    "demo": create_demo_agent,
    "fundraising": create_fundraising_agent,
    "activities": create_activities_agent,
    "accommodation": create_accommodation_agent
}


def create_specialized_agents(required_agents: List[str]) -> Dict[str, Agent]:
    """Create specialized agents based on the required agent types."""
    agents = {}
    
    for agent_type in required_agents:
        if agent_type in AGENT_CREATORS:
            agents[agent_type] = AGENT_CREATORS[agent_type]()
        else:
            # Create a generic agent for unknown types
            agents[agent_type] = Agent(
                name=f"{agent_type.title()} Specialist",
                instructions=f"You are a specialist in {agent_type} planning and coordination."
            )
    
    return agents
