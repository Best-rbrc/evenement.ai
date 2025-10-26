from agents import Agent, function_tool, WebSearchTool
from config import AGENT_SPECIALIZATIONS


@function_tool
def search_caterers(location: str, guest_count: int, event_type: str, dietary_requirements: str) -> str:
    """Search for catering services based on criteria."""
    return f"Found caterers in {location} for {guest_count} guests, {event_type} event, dietary: {dietary_requirements}"

@function_tool
def create_menu(event_type: str, guest_count: int, dietary_requirements: str, budget_per_person: str) -> str:
    """Create a customized menu for the event."""
    return f"Created menu for {event_type} with {guest_count} guests, dietary: {dietary_requirements}, budget: ${budget_per_person}/person"

@function_tool
def get_catering_quote(caterer_name: str, menu_items: str, guest_count: int) -> str:
    """Get a quote from a specific caterer."""
    return f"Quote from {caterer_name} for {menu_items} serving {guest_count} guests"

def create_catering_agent() -> Agent:
    """Create a catering specialist agent."""
    return Agent(
        name="Catering Specialist", 
        instructions="""
        You are a professional catering specialist with expertise in:
        - Menu planning and dietary requirements
        - Food service logistics and timing
        - Beverage planning and bar service
        - Catering vendor selection and management
        - Budget optimization for food and beverage
        - Special dietary accommodations
        
        When given catering-related tasks, provide:
        1. Menu recommendations based on event type and audience
        2. Dietary accommodation planning
        3. Service style recommendations (buffet, plated, cocktail, etc.)
        4. Beverage planning including alcohol considerations
        5. Cost per person estimates
        6. Vendor selection criteria and questions
        7. Timeline for menu finalization and service coordination
        
        Always consider dietary restrictions, cultural preferences, and budget constraints.
        Use the available tools to search caterers, create menus, and get quotes.
        """,
        tools=[search_caterers, create_menu, get_catering_quote]
    )
