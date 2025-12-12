from agents import Agent, function_tool, WebSearchTool, AgentOutputSchema
from workflows.pydantic_schemas import SpeakersOutput

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
    """Create a speakers specialist agent.
    
    Uses structured outputs to ensure valid JSON responses.
    """
    return Agent(
        name="Speakers Specialist",
         output_type=AgentOutputSchema(SpeakersOutput, strict_json_schema=False),
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
        
        CRITICAL OUTPUT REQUIREMENTS:
        1. Return ONLY a valid JSON object - NO markdown, NO code blocks, NO extra text
        2. Ensure ALL required fields are present and valid
        3. Each speaker object MUST have all required fields
        4. Validate complete JSON before returning
        5. NO extra data or trailing content after JSON
        6. Keep response concise to avoid parsing issues
        
        """,
        tools=[search_speakers, get_speaker_details, coordinate_speaker_logistics]
    )

