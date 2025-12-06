from agents import Agent, function_tool, WebSearchTool

@function_tool
def create_event_schedule(event_name: str, event_duration: str, session_count: int) -> str:
    """Create a detailed event schedule."""
    return f"Created schedule for {event_name}: {event_duration} with {session_count} sessions"

@function_tool
def plan_session_flow(session_name: str, duration: str, speaker_name: str) -> str:
    """Plan the flow for a specific session."""
    return f"Planned {session_name} ({duration}) with {speaker_name}"

@function_tool
def create_break_schedule(break_duration: str, break_count: int) -> str:
    """Create break schedule for the event."""
    return f"Created {break_count} breaks of {break_duration} each"

def create_programme_agent() -> Agent:
    """Create a programme specialist agent."""
    return Agent(
        name="Programme Specialist",
        instructions="""
        You are a professional programme coordinator with expertise in:
        - Event scheduling and timeline creation
        - Session planning and flow optimization
        - Break and networking time planning
        - Technical requirements coordination
        - Programme logistics and timing
        - Contingency planning for delays
        
        When given programme-related tasks, provide:
        1. Detailed event schedule with timing
        2. Session flow and transition planning
        3. Break and networking time optimization
        4. Technical setup requirements and timing
        5. Speaker and presenter coordination
        6. Contingency plans for timing issues
        7. Programme materials and handouts planning
        
        Always consider attendee engagement, speaker needs, and logistical constraints.
        Use the available tools to create schedules, plan sessions, and coordinate breaks.
        """,
        tools=[create_event_schedule, plan_session_flow, create_break_schedule]
    )

