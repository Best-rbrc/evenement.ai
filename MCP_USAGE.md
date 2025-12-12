# FastMCP Server Usage Guide

Quick guide for using the AI Event Planner as an MCP server.

## Installation

```bash
git clone https://github.com/Adrien-Z/AI-Event-Planner-Agent.git
cd AI-Event-Planner-Agent
uv sync  # or: pip install -e .
```

Verify installation:
```bash
uv run event-planner-mcp --help
# or
uv run python -m custom_mcp_servers.fastmcp_server --help
```

## Configuration

Set environment variables (create `.env` file or export):

```bash
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional
PLAN_EVENT_FORM_MODE=skip  # Options: skip, unsandboxed, sandboxed
```

## Connect to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "event-planner": {
      "command": "uv",
      "args": ["run", "python", "-m", "custom_mcp_servers.fastmcp_server"],
      "cwd": "/path/to/AI-Event-Planner-Agent",
      "env": {
        "OPENAI_API_KEY": "sk-proj-your-key-here"
      }
    }
  }
}
```

Replace `/path/to/AI-Event-Planner-Agent` with your actual path. Restart Claude Desktop.

## Available Tools

- **`plan_event`** - Plan a complete event (requires `event_name`, `event_type`)
- **`list_event_outputs`** - List generated files
- **`read_event_output`** - Read file contents (ICS, PDF, etc.)

## Example

```python
import asyncio
from agents import MCPServerStdio

async def main():
    async with MCPServerStdio(
        "python",
        args=["-m", "custom_mcp_servers.fastmcp_server"],
        cwd="/path/to/AI-Event-Planner-Agent",
        env={"OPENAI_API_KEY": "sk-proj-..."}
    ) as mcp:
        result = await mcp.call_tool("plan_event", {
            "event_details": {
                "event_name": "Tech Conference 2024",
                "event_type": "conference",
                "event_date": "2024-06-15",
                "location_preference": "San Francisco, CA",
                "budget_range": "$50,000-$75,000",
                "guest_count": "200-300"
            }
        })
        print(result)

asyncio.run(main())
```

## Troubleshooting

**Missing dependencies:** Run `uv sync` or `pip install -e .`

**Missing API key:** Set `OPENAI_API_KEY` environment variable

**Command not found:** Use `uv run python -m custom_mcp_servers.fastmcp_server` instead

**Need help?** Run `event-planner-mcp --help` for command-line options and usage information.

For more details, see `README.md` and `ARCHITECTURE.md`.
