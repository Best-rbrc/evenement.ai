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
        instructions="Catering specialist. Recommend food/beverage options with costs. Consider event type, guest count, dietary needs, venue kitchen. Return JSON with options, costs, logistics.",
        tools=[search_caterers, create_menu, get_catering_quote]
    )
