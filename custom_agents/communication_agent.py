from agents import Agent, function_tool, WebSearchTool

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
    """Create a communication specialist agent."""
    return Agent(
        name="Communication Specialist",
        instructions="""
        Communication specialist. Handle marketing, invitations, attendee communications. Create marketing strategy, designs, social media plans. Return JSON with campaign details, timelines.
        """,
        tools=[create_invitation_design, plan_marketing_campaign, create_communication_templates]
    )
