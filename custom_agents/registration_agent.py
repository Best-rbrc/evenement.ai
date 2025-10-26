from agents import Agent, function_tool, WebSearchTool

@function_tool
def setup_registration_system(event_name: str, attendee_count: int, registration_type: str) -> str:
    """Set up a registration system for the event."""
    return f"Set up {registration_type} registration system for {event_name} with {attendee_count} attendees"

@function_tool
def create_registration_form(event_type: str, required_fields: str) -> str:
    """Create a registration form for the event."""
    return f"Created registration form for {event_type} with fields: {required_fields}"

@function_tool
def design_badges(event_name: str, badge_type: str, attendee_count: int) -> str:
    """Design badges for the event."""
    return f"Designed {badge_type} badges for {event_name} ({attendee_count} attendees)"

def create_registration_agent() -> Agent:
    """Create a registration specialist agent."""
    return Agent(
        name="Registration Specialist",
        instructions="""
        You are a professional registration coordinator with expertise in:
        - Registration system setup and management
        - Attendee data collection and management
        - Check-in process and logistics
        - Badge and credential design
        - Registration timeline and communication
        - Data privacy and security compliance
        
        When given registration-related tasks, provide:
        1. Registration system recommendations
        2. Data collection strategy and forms
        3. Check-in process and logistics planning
        4. Badge and credential design
        5. Registration timeline and communication plan
        6. Data privacy and security measures
        7. Backup registration and check-in procedures
        
        Always consider attendee experience, data security, and event scale.
        Use the available tools to set up systems, create forms, and design badges.
        """,
        tools=[setup_registration_system, create_registration_form, design_badges]
    )

