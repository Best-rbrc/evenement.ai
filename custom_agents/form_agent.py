import asyncio
import os
import json
import re
import time
import random
import contextlib
from agents import Agent
from agents.mcp import MCPServerStdio
from agents.model_settings import ModelSettings
from agents import Runner

TALLY_MCP_URL = "https://api.tally.so/mcp"


def create_form_agent(mcp_servers=None) -> Agent:
    """Create a Tally form agent that generates registration forms for events.
    
    Args:
        mcp_servers: Optional MCPServers instance for sandboxed form data handling
    
    Returns:
        Agent configured to create event registration forms using Tally MCP tools
    """
    
    # Setup MCP servers
    servers_to_use = []
    
    if mcp_servers is not None:
        # Use sandboxed MCP server if provided
        servers_to_use = [mcp_servers]
    else:
        # Fallback to direct Tally MCP (not sandboxed)
        tally_server = MCPServerStdio({
            "command": "npx",
            "args": [
                "mcp-remote",
                TALLY_MCP_URL,
                "--header",
                f"Authorization: Bearer {os.getenv('TALLY_API_KEY', '')}",
            ],
        })
        # Ensure the server is connected before use
        if hasattr(tally_server, "connect"):
            connect_method = getattr(tally_server, "connect")
            if callable(connect_method):
                try:
                    # Handle both sync and async connect implementations without warnings
                    if asyncio.iscoroutinefunction(connect_method):
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            loop.create_task(connect_method())
                        else:
                            loop.run_until_complete(connect_method())
                    else:
                        connect_method()
                except Exception:
                    pass  # Fail silently if connect() is async or fails
        
        servers_to_use = [tally_server]

    # Configure model with rate limit friendly settings
    model_settings = ModelSettings(
        max_tokens=8000,  # Limit response tokens to stay under rate limits
        temperature=0.7
    )

    agent_kwargs = {
        "name": "Form Creation Specialist",
        "instructions": """
        You are a specialist in designing and managing online forms.

        Your sole responsibility is to:
        - Create event registration/RSVP forms tailored to the specific event
        - Design forms with appropriate fields based on event type and requirements
        - Include essential fields: name, email, contact info, attendance confirmation
        - Add event-specific fields (dietary restrictions for catered events, company for corporate events, etc.)
        - Make the form user-friendly and professional
        - Save the form and return the public sharing URL
        
        CRITICAL URL REQUIREMENTS:
        - The "form_url" field MUST be a valid, complete URL starting with https://
        - DO NOT include partial URLs, relative paths, or plain text descriptions
        - Valid format: "https://tally.so/r/xxxxx" (where xxxxx is the actual form ID)
        - If form creation fails, use empty string "" for form_url
        
        CRITICAL: After successful form creation, return ONLY valid JSON in this exact format:
        {"form_url": "https://tally.so/r/xxxxx", "status": "success", "form_details": "brief description"}
        
        Do not include any other text, explanations, or markdown formatting in your response.

        You have NO other duties. Do not answer general questions or perform unrelated tasks.
        """,
        "model_settings": model_settings,
    }
    
    if servers_to_use:
        agent_kwargs["mcp_servers"] = servers_to_use
    
    return Agent(**agent_kwargs)


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


async def _run_form_once(prompt: str, mcp_servers=None, form_model_env: str = "FORM_MODEL"):
    """Run the form agent once, respecting optional model override, ensuring MCP servers are connected.
    
    Args:
        prompt: The prompt for the form agent
        mcp_servers: Optional MCPServers instance for sandboxing
        form_model_env: Environment variable for model override
    """
    prev_model = os.environ.get("OPENAI_MODEL")
    form_model = os.environ.get(form_model_env)
    if form_model:
        os.environ["OPENAI_MODEL"] = form_model
    try:
        agent = create_form_agent(mcp_servers=mcp_servers)
        servers = getattr(agent, "mcp_servers", []) or []
        if servers:
            async with contextlib.AsyncExitStack() as stack:
                for server in servers:
                    await stack.enter_async_context(server)
                result = await Runner.run(agent, prompt)
                return result
        # Fallback if no servers are attached
        return await Runner.run(agent, prompt)
    finally:
        if form_model:
            if prev_model is None:
                os.environ.pop("OPENAI_MODEL", None)
            else:
                os.environ["OPENAI_MODEL"] = prev_model


def run_form_with_retries(prompt: str, mcp_servers=None, max_retries: int = 5) -> tuple[object, str | None]:
    """Run the form agent with simple backoff for transient MCP issues.
    
    Args:
        prompt: The prompt for the form agent
        mcp_servers: Optional MCPServers instance for sandboxing
        max_retries: Maximum number of retries

    Returns a tuple of (result, last_error_text). The caller can decide how to handle failures.
    """
    form_result = None
    last_exc_text = None

    for attempt in range(max_retries):
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                form_result = loop.create_task(_run_form_once(prompt, mcp_servers=mcp_servers))
                return form_result, None

            form_result = loop.run_until_complete(_run_form_once(prompt, mcp_servers=mcp_servers))
            break
        except Exception as e:
            last_exc_text = str(e)
            is_transient = (
                "rate_limit" in last_exc_text.lower()
                or "StreamableHTTPError" in last_exc_text
                or "SSE" in last_exc_text
                or " 524" in last_exc_text
            )
            if is_transient and attempt < max_retries - 1:
                base_wait = 2 ** attempt
                reason = "rate limit" if "rate_limit" in last_exc_text.lower() else "remote connection"
                wait_time = max(5.0, min(30.0, base_wait * 1.5))
                wait_time += random.uniform(0.5, 1.2)
                print(f"⏳ Transient {reason} issue. Waiting {wait_time:.2f}s before retry...\n")
                time.sleep(wait_time)
                continue
            break

    if form_result is not None:
        return form_result, last_exc_text

    # Fallback error object to keep downstream logic stable
    return type('obj', (object,), {'final_output': '{"status": "error", "message": "Form creation failed"}'})(), last_exc_text
