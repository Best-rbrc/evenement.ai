"""Custom specialized agents for event planning.

This package exports factory functions for creating specialized agents
for different aspects of event planning (venue, catering, speakers, etc.).
"""

from custom_agents.venue_agent import create_venue_agent
from custom_agents.catering_agent import create_catering_agent
from custom_agents.speaker_agent import create_speakers_agent
from custom_agents.programme_agent import create_programme_agent
from custom_agents.communication_agent import create_communication_agent
from custom_agents.registration_agent import create_registration_agent
from custom_agents.activities_agent import create_activities_agent
from custom_agents.entertainment_agent import create_entertainment_agent

# Import from archive folder if needed (these are optional/archived agents)
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

__all__ = [
    "create_venue_agent",
    "create_catering_agent",
    "create_speakers_agent",
    "create_programme_agent",
    "create_communication_agent",
    "create_registration_agent",
    "create_activities_agent",
    "create_entertainment_agent",
    "create_decoration_agent",
    "create_photography_agent",
    "create_music_agent",
    "create_seating_agent",
    "create_materials_agent",
    "create_networking_agent",
    "create_media_agent",
    "create_demo_agent",
    "create_sponsors_agent",
    "create_accommodation_agent",
]
