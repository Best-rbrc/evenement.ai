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
        Programme specialist. Create event schedule and session flow. Plan timing, breaks, networking, technical setup. Return JSON with timeline, sessions, logistics.
        """,
        tools=[create_event_schedule, plan_session_flow, create_break_schedule]
    )

