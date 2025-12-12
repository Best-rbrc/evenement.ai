from agents import Agent, function_tool, WebSearchTool, AgentOutputSchema
from workflows.pydantic_schemas import CommunicationOutput

@function_tool
def create_invitation_design(event_name: str, event_type: str, event_date: str) -> str:
    """Create invitation design for the event."""
    return f"Created invitation design for {event_name} ({event_type}) on {event_date}"

@function_tool
def plan_marketing_campaign(event_name: str, target_audience: str, budget: str) -> str:
    """Plan a marketing campaign for the event."""
    return f"Planned marketing campaign for {event_name} targeting {target_audience} with budget {budget}"

@function_tool
def create_communication_templates(event_type: str, communication_purpose: str) -> str:
    """Create communication templates for the event."""
    return f"Created {communication_purpose} templates for {event_type} event"

def create_communication_agent() -> Agent:
    """Create a communication specialist agent.
    
    Uses structured outputs to ensure valid JSON responses.
    """
    return Agent(
        name="Communication Specialist",
         output_type=AgentOutputSchema(CommunicationOutput, strict_json_schema=False),
        instructions="""
        You are a professional communication specialist with expertise in:
        - Event marketing and promotion
        - Invitation design and distribution
        - Attendee communication and updates
        - Social media and digital marketing
        - Press and media relations
        - Post-event communication and follow-up
        
        When given communication-related tasks, provide:
        1. Marketing strategy and promotional timeline
        2. Invitation design and distribution plan
        3. Communication templates and messaging
        4. Social media content and posting schedule
        5. Media outreach and press release strategy
        6. Attendee communication and updates
        7. Post-event follow-up and feedback collection
        
        Always consider the target audience, event goals, and available communication channels.
        Use the available tools to create invitations, plan marketing, and create templates.
        """,
        tools=[create_invitation_design, plan_marketing_campaign, create_communication_templates]
    )
