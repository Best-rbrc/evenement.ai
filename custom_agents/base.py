"""Specialized agents for different aspects of event planning."""
from typing import Dict, List
from agents import Agent

# Import agent factories directly from their modules to avoid circular import
from custom_agents.venue_agent import create_venue_agent
from custom_agents.catering_agent import create_catering_agent
from custom_agents.speaker_agent import create_speakers_agent
from custom_agents.programme_agent import create_programme_agent
from custom_agents.communication_agent import create_communication_agent
from custom_agents.registration_agent import create_registration_agent
from custom_agents.activities_agent import create_activities_agent
from custom_agents.entertainment_agent import create_entertainment_agent
from custom_agents.calendar_agent import create_calendar_agent
from custom_agents.form_agent import create_form_agent
from custom_agents.budgeting_agent import create_budgeting_agent

# Optional archived agents - import with fallbacks
try:
    from custom_agents.archive.decoration_agent import create_decoration_agent
except ImportError:
    create_decoration_agent = None

try:
    from custom_agents.archive.photography_agent import create_photography_agent
except ImportError:
    create_photography_agent = None

try:
    from custom_agents.archive.music_agent import create_music_agent
except ImportError:
    create_music_agent = None

try:
    from custom_agents.archive.seating_agent import create_seating_agent
except ImportError:
    create_seating_agent = None

try:
    from custom_agents.archive.materials_agent import create_materials_agent
except ImportError:
    create_materials_agent = None

try:
    from custom_agents.archive.networking_agent import create_networking_agent
except ImportError:
    create_networking_agent = None

try:
    from custom_agents.archive.media_agent import create_media_agent
except ImportError:
    create_media_agent = None

try:
    from custom_agents.archive.demo_agent import create_demo_agent
except ImportError:
    create_demo_agent = None

try:
    from custom_agents.archive.sponsor_agent import create_sponsors_agent
except ImportError:
    create_sponsors_agent = None

try:
    from custom_agents.archive.accomodation_agent import create_accommodation_agent
except ImportError:
    create_accommodation_agent = None

# Agent creation mapping
AGENT_CREATORS = {
    "venue": create_venue_agent,
    "catering": create_catering_agent,
    "speakers": create_speakers_agent,
    "programme": create_programme_agent,
    "communication": create_communication_agent,
    "registration": create_registration_agent,
    "activities": create_activities_agent,
    "entertainment": create_entertainment_agent,
    "budgeting": create_budgeting_agent,
    "calendar": create_calendar_agent,
    "form": create_form_agent,
}

# Add optional archived agents only if they were successfully imported
if create_decoration_agent:
    AGENT_CREATORS["decoration"] = create_decoration_agent
if create_photography_agent:
    AGENT_CREATORS["photography"] = create_photography_agent
if create_music_agent:
    AGENT_CREATORS["music"] = create_music_agent
if create_seating_agent:
    AGENT_CREATORS["seating"] = create_seating_agent
if create_materials_agent:
    AGENT_CREATORS["materials"] = create_materials_agent
if create_networking_agent:
    AGENT_CREATORS["networking"] = create_networking_agent
if create_media_agent:
    AGENT_CREATORS["media"] = create_media_agent
if create_demo_agent:
    AGENT_CREATORS["demo"] = create_demo_agent
if create_sponsors_agent:
    AGENT_CREATORS["sponsors"] = create_sponsors_agent
if create_accommodation_agent:
    AGENT_CREATORS["accommodation"] = create_accommodation_agent


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
