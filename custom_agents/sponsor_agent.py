from agents import Agent, function_tool, WebSearchTool

@function_tool
def create_sponsorship_packages(event_name: str, package_levels: str, pricing: str) -> str:
    """Create sponsorship packages for the event."""
    return f"Created {package_levels} sponsorship packages for {event_name} with pricing: {pricing}"

@function_tool
def recruit_sponsors(event_type: str, target_industries: str, budget_goal: str) -> str:
    """Recruit sponsors for the event."""
    return f"Recruiting sponsors for {event_type} targeting {target_industries} with goal: {budget_goal}"

@function_tool
def create_sponsor_benefits(sponsor_level: str, event_reach: str, benefits: str) -> str:
    """Create benefits package for sponsors."""
    return f"Created {sponsor_level} benefits for {event_reach} reach: {benefits}"

def create_sponsors_agent() -> Agent:
    """Create a sponsors specialist agent."""
    return Agent(
        name="Sponsors Specialist",
        instructions="""
        You are a professional sponsors coordinator with expertise in:
        - Sponsor recruitment and relationship management
        - Sponsorship packages and benefits
        - Sponsor contracts and deliverables
        - Sponsor recognition and branding
        - Revenue optimization and pricing
        - Sponsor communication and coordination
        
        When given sponsor-related tasks, provide:
        1. Sponsor recruitment strategy and target identification
        2. Sponsorship package design and pricing
        3. Sponsor contract terms and deliverables
        4. Sponsor recognition and branding opportunities
        5. Revenue projections and optimization strategies
        6. Sponsor communication and coordination timeline
        7. Sponsor fulfillment and post-event follow-up
        
        Always consider sponsor value proposition, event reach, and competitive landscape.
        Use the available tools to create packages, recruit sponsors, and design benefits.
        """,
        tools=[create_sponsorship_packages, recruit_sponsors, create_sponsor_benefits]
    )

