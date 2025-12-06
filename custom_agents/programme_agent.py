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
        
        CRITICAL OUTPUT REQUIREMENTS:
        1. Return ONLY a valid JSON object - NO markdown, NO code blocks, NO explanations
        2. Ensure ALL required fields are present
        3. Use proper JSON types (strings, numbers, arrays, objects)
        4. NO trailing commas
        5. Validate complete JSON before returning
        6. NO extra text before or after JSON
        
        REQUIRED STRUCTURE:
{
  "summary": "string",
  "programme_recommendations": {
    "options": [
      {
        "name": "string",
        "description": "string",
        "capacity": "string",
        "cost": "string",
        "amenities": ["string"],
        "dependencies": ["string"]
      }
    ],
    "timeline_and_logistics": ["string"],
    "session_and_flow": {
      "morning_session": "string",
      "afternoon_session": "string"
    },
    "breaks_networking": ["string"],
    "technical_and_materials_requirements": ["string"],
    "contingency_plans": ["string"],
    "top_recommendation": {
      "option": "string",
      "rationale": "string",
      "dependencies": ["string"]
    },
    "backup_option": {
      "option": "string",
      "rationale": "string"
    }
  },
  "next_steps": ["string"]
}
        """,
        tools=[create_event_schedule, plan_session_flow, create_break_schedule]
    )

