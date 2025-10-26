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
        You are a professional speakers coordinator with expertise in:
        - Speaker recruitment and selection
        - Speaker contracts and logistics
        - Presentation requirements and technical needs
        - Speaker travel and accommodation
        - Speaker communication and briefing
        - Backup speaker planning
        
        When given speaker-related tasks, provide:
        1. Speaker recommendations based on event theme and audience
        2. Speaker recruitment strategies and outreach
        3. Contract negotiation points and speaker fees
        4. Technical requirements and presentation setup
        5. Travel and accommodation coordination
        6. Speaker briefing and communication plans
        7. Timeline for speaker confirmation and preparation
        
        Always consider the event's educational goals, audience expertise level, and budget.
        Use the available tools to search speakers, get details, and coordinate logistics.
        """,
        tools=[search_speakers, get_speaker_details, coordinate_speaker_logistics]
    )

