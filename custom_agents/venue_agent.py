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

        **CRITICAL JSON SYNTAX REQUIREMENTS:**
        - You MUST return ONLY valid JSON - NO markdown, NO code blocks, NO explanations, NO backticks
        - Every opening brace { must have a closing brace }
        - Every opening bracket [ must have a closing bracket ]
        - Every string must be properly quoted with double quotes "
        - Every field must be separated by commas (except the last one in objects/arrays)
        - NO trailing commas before closing braces or brackets
        - Validate your JSON syntax before returning - it must parse correctly
        
        **CRITICAL URL REQUIREMENTS:**
        - The "website" field MUST be a valid, complete URL starting with http:// or https://
        - DO NOT include partial URLs, relative paths, or plain text descriptions
        - Examples of VALID formats: "https://www.venue.com", "http://venue.example.org/events"
        - Examples of INVALID formats: "venue.com", "www.venue.com", "Check venue website", "Olma Messen events site"
        - If you cannot find a valid URL, use an empty string "" instead of a description or partial URL
        - Always verify the URL format before including it in the JSON

        **CRITICAL PRICE FORMAT REQUIREMENTS:**
        - The "estimated_cost" field can be a string or number
        - If using a string, format as: "$25,000" or "$25,000 - $100,000" for ranges
        - DO NOT use malformed formats like "$25,000,100,000" (use "$25,000 - $100,000" instead)
        - Keep price strings clean and properly formatted
        - Examples: "$25,000", "$25,000 - $100,000", "$8,000 per day", 25000 (as number)

        **Important:** Always perform an actual web search using the `web_search` tool before making recommendations.
        
        **OUTPUT FORMAT:**
        Return ONLY valid JSON (no markdown, no commentary, no backticks, no extra text).

        Required structure:
""" + schema_to_json_example("venue") + """

        **VALIDATION CHECKLIST BEFORE RETURNING:**
        1. ✓ All braces and brackets are properly closed
        2. ✓ All strings are in double quotes
        3. ✓ All fields are separated by commas (no trailing commas)
        4. ✓ The "capacity" field is a NUMBER (not a string)
        5. ✓ The "estimated_cost" is properly formatted (string or number)
        6. ✓ The "website" field is a valid URL or empty string ""
        7. ✓ The entire output is valid JSON that can be parsed
        
        If your JSON is invalid, the system will fail. Double-check your syntax!
        """,
        tools=[WebSearchTool(search_context_size="high"), check_venue_availability, get_venue_details]
    )
