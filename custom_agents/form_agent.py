import os
import json
import re
from agents import Agent
from agents.mcp import MCPServerStdio
from agents.model_settings import ModelSettings

TALLY_MCP_URL = "https://api.tally.so/mcp"


def create_form_agent() -> Agent:
    """Create a Tally form agent that generates registration forms for events.
    
    Returns:
        Agent configured to create event registration forms using Tally MCP tools
    """
    # Resolve cross-platform npx command (Windows uses npx.cmd)
    npx_command = "npx.cmd" if os.name == "nt" else "npx"
    tally_server = MCPServerStdio({
        "command": npx_command,
        "args": [
            "mcp-remote",
            TALLY_MCP_URL,
            "--header",
            f"Authorization: Bearer {os.getenv('TALLY_API_KEY', '')}",
        ],
    })

    # Safely connect proactively to avoid "Server not initialized" at first use.
    # Works with Python 3.13 where no default loop exists unless we create one.
    try:
        if hasattr(tally_server, "connect_sync"):
            tally_server.connect_sync()
        elif hasattr(tally_server, "connect"):
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            # Only run if the loop is not running
            if not loop.is_running():
                loop.run_until_complete(tally_server.connect())
            else:
                # If already running, best effort: schedule and wait briefly
                async def _do_connect():
                    try:
                        await tally_server.connect()
                    except Exception:
                        pass
                asyncio.create_task(_do_connect())
    except Exception as _e:
        # Emit debug info if requested instead of silently swallowing
        if os.getenv("TALLY_DEBUG"):
            print(f"[TALLY_DEBUG] Initial MCP connect failed: {_e}")
        # Allow runtime to retry later

    # Configure model with rate limit friendly settings
    model_settings = ModelSettings(
        max_tokens=8000,  # Limit response tokens to stay under rate limits
        temperature=0.7
    )

    return Agent(
        name="Form Creation Specialist",
        instructions="""
        You are a specialist in designing and managing online forms using the Tally MCP tools.

        Your sole responsibility is to:
        - Create event registration/RSVP forms tailored to the specific event
        - Design forms with appropriate fields based on event type and requirements
        - Include essential fields: name, email, contact info, attendance confirmation
        - Add event-specific fields (dietary restrictions for catered events, company for corporate events, etc.)
        - Make the form user-friendly and professional
        - Save the form and return the public sharing URL
        
        CRITICAL: After successful form creation, return ONLY valid JSON in this exact format:
        {"form_url": "https://tally.so/r/xxxxx", "status": "success", "form_details": "brief description"}
        
        Do not include any other text, explanations, or markdown formatting in your response.

        You have NO other duties. Do not answer general questions or perform unrelated tasks.
        Use the connected Tally MCP tools exclusively when taking any action.
        """,
        mcp_servers=[tally_server],
        model_settings=model_settings,
    )


def extract_form_url_from_output(output: str) -> dict:
    """Extract form URL and status from agent output.
    
    Args:
        output: Raw output from the form agent
        
    Returns:
        Dictionary with form_url, status, and other details
    """
    try:
        # Try to extract JSON from the output
        json_match = re.search(r'\{[^{}]*"form_url"[^{}]*\}', output)
        if json_match:
            json_data = json.loads(json_match.group())
            return json_data
        else:
            # Fallback: look for a tally.so URL
            url_match = re.search(r'https://tally\.so/r/[a-zA-Z0-9]+', output)
            if url_match:
                return {
                    "form_url": url_match.group(),
                    "status": "success",
                    "form_details": "Form created successfully"
                }
    except (json.JSONDecodeError, AttributeError):
        pass
    
    # Return error if we couldn't extract anything
    return {
        "status": "error",
        "message": "Could not extract form URL from output",
        "raw_output": output
    }
