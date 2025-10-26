import os
from agents import Agent
from agents.mcp import MCPServerStdio

TALLY_MCP_URL = "https://api.tally.so/mcp"


def create_form_agent() -> Agent:
    tally_server = MCPServerStdio({
        "command": "npx",
        "args": [
            "mcp-remote",
            TALLY_MCP_URL,
            "--header",
            f"Authorization: Bearer {os.getenv('TALLY_API_KEY', '')}",
        ],
    })

    return Agent(
        name="Form Creation Specialist",
        instructions="""
        You are a specialist in designing and managing online forms using the connected
        Tally MCP tools.

        Your sole responsibility is to:
        - Create, edit, or update Tally forms (RSVPs, surveys, feedback, registration, etc.).
        - Define fields clearly (label, required/optional, field type).
        - Save the form and return the public sharing URL.
        - Ask one concise clarification question if necessary before creation.

        You have NO other duties. Do not answer general questions or perform unrelated tasks.
        Use the connected Tally MCP tools exclusively when taking any action.
        """,
        mcp_servers=[tally_server],
    )
