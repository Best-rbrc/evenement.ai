from agents import Agent, function_tool, WebSearchTool
from workflows.schemas import schema_to_json_example

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
        instructions="""
        You are a professional venue specialist.

        Use the WebSearchTool to find **real venues** that match the given:
        - Event location
        - Capacity
        - Budget
        - Event type (e.g., wedding, conference)
        - Date and accessibility preferences

        For each venue, extract:
        - Name and website
        - Capacity and amenities
        - Estimated cost (and currency)
        - Availability if possible
        - Key reasoning why it fits
        - Backup alternatives

        **CRITICAL URL REQUIREMENTS:**
        - The "website" field MUST be a valid, complete URL starting with http:// or https://
        - DO NOT include partial URLs, relative paths, or plain text descriptions
        - Examples of VALID formats: "https://www.venue.com", "http://venue.example.org/events"
        - Examples of INVALID formats: "venue.com", "www.venue.com", "Check venue website", "Olma Messen events site"
        - If you cannot find a valid URL, use an empty string "" instead of a description or partial URL
        - Always verify the URL format before including it in the JSON

        **Important:** Always perform an actual web search using the `web_search` tool before making recommendations.
        
Return ONLY valid JSON (no markdown, no commentary, no backticks).

Required structure:
""" + schema_to_json_example("venue") + """

Note: The "capacity" field MUST be a number, not a string. The "estimated_cost" can be either a string or number.
        """,
        tools=[WebSearchTool(search_context_size="high"), check_venue_availability, get_venue_details]
    )
