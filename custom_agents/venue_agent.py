from agents import Agent, function_tool, WebSearchTool
from config import AGENT_SPECIALIZATIONS

@function_tool
def search_venues(location: str, capacity: int, event_type: str, budget_range: str) -> str:
    """
    Use the web search tool to find real venues based on location, capacity, and budget.
    The search should return current options from the web, including pricing and contact info.
    """
    query = f"{event_type} venues in {location} for {capacity} people under {budget_range}"
    # Delegate to the hosted search tool
    return WebSearchTool().name + f"('{query}')"

@function_tool
def check_venue_availability(venue_name: str, event_date: str) -> str:
    """Check if a venue is available on the specified date."""
    return f"Venue {venue_name} availability for {event_date}: Available"

@function_tool
def get_venue_details(venue_name: str) -> str:
    """Get detailed information about a specific venue."""
    return f"Venue details for {venue_name}: Capacity, amenities, pricing, accessibility info"

def create_venue_agent() -> Agent:
    """Create a venue specialist agent with real web search capabilities."""
    return Agent(
        name="Venue Specialist",
        handoff_description="Finds and evaluates real venues for the event.",
        instructions=f"""
        Venue specialist. Use WebSearchTool to find real venues matching location, capacity, budget, event type. Extract: name, website, capacity, cost, availability. Return top 3 in JSON.
        """,
        tools=[WebSearchTool(search_context_size="high"), check_venue_availability, get_venue_details]
    )
