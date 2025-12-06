"""Test the MCP server with direct tool calls and LLM agent integration."""
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

# .env laden (Projektroot)
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(ENV_PATH)


async def main():
    choice = input("Modus wählen: 1 = Direktes Tool, 2 = LLM-Agent + Tool (Standard 1): ").strip() or "1"

    # MCP-Server-Definition: starte deinen FastMCP-Server per stdio
    mcp_server = MCPServerStdio(
        name="event-planner",
        params={
            "command": "python",
            "args": ["-m", "custom_mcp_servers.fastmcp_server"],
        },
        client_session_timeout_seconds=900,  # workflow can take several minutes
    )

    async with mcp_server:
        if choice == "2":
            # Beispiel: gleicher Server über einen Agenten nutzen (LLM orchestriert den Tool-Call)
            agent = Agent(
                name="Planner Client Agent",
                model="gpt-4.1-mini",
                instructions="""You have access to the MCP tool 'plan_event'.

When calling plan_event, you MUST provide the argument 'event_details' as a dictionary with at least:
- event_name (required string)
- event_type (required string)

Optional fields: event_date, location_preference, guest_count, budget, special_requirements.

Example tool call structure:
{
  "event_details": {
    "event_name": "Tech Conference Zurich",
    "event_type": "conference",
    "event_date": "2026-05-10",
    "location_preference": "Zurich",
    "guest_count": 120,
    "budget": "$25k",
    "special_requirements": "hybrid streaming"
  }
}

Extract the event details from the user's input and call plan_event with the properly structured event_details argument.""",
                mcp_servers=[mcp_server],
            )

            agent_input = "Plane eine eintägige Tech-Konferenz in Zürich für ca. 120 Personen am 2026-05-10."
            agent_result = await Runner.run(agent, agent_input)

            print("\n===== AGENT-ANTWORT (LLM+MCP) =====\n")
            try:
                print(agent_result.final_output)
            except Exception:
                print(agent_result)
        else:
            # Direkter Tool-Call (ohne LLM-Agent), damit Schema sicher erfüllt wird
            payload = {
                "event_details": {
                    "event_name": "Tech-Konferenz St. Gallen",
                    "event_type": "conference",
                    "event_date": "2026-05-10",
                    "location_preference": "St. Gallen",
                    "guest_count": 80,
                    "budget": "$20k",
                    "special_requirements": "hybrid streaming",
                }
            }

            result = await mcp_server.call_tool("plan_event", payload)

            print("\n===== TOOL-RESULT =====\n")
            # result.content is a list of content parts; first is text json
            if result.content:
                try:
                    text = result.content[0].text
                    parsed = json.loads(text)
                    print(json.dumps(parsed, indent=2, ensure_ascii=False))
                except Exception:
                    print(result.content)
            else:
                print(result)


if __name__ == "__main__":
    asyncio.run(main())