from agents import Agent, function_tool, WebSearchTool

@function_tool
def search_speakers(topic: str, event_type: str, budget_range: str) -> str:
    """Search for speakers based on topic and event requirements."""
    return f"Found speakers for {topic} at {event_type} event with budget {budget_range}"

@function_tool
def get_speaker_details(speaker_name: str) -> str:
    """Get detailed information about a specific speaker."""
    return f"Speaker details for {speaker_name}: Bio, expertise, speaking fees, availability"

@function_tool
def coordinate_speaker_logistics(speaker_name: str, event_date: str, location: str) -> str:
    """Coordinate travel and accommodation for a speaker."""
    return f"Coordinated logistics for {speaker_name} for {event_date} in {location}"

def create_speakers_agent() -> Agent:
    """Create a speakers specialist agent."""
    return Agent(
        name="Speakers Specialist",
        instructions="""
        Speakers specialist. Recommend speakers based on event theme/audience. Handle recruitment, contracts, logistics, travel. Return JSON with speaker options, costs, requirements.
        """,
        tools=[search_speakers, get_speaker_details, coordinate_speaker_logistics]
    )

