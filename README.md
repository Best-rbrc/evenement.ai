# AI Event Planner - MCP Server

An intelligent event planning system using OpenAI Agents that coordinates specialized AI agents to create comprehensive event plans.

## Quick Start - Installation

Install from GitHub releases:
```bash
pip install https://github.com/Adrien-Z/AI-Event-Planner-Agent/releases/download/v1.0.0/event_planner_mcp-1.0.0-py3-none-any.whl
```

## API Keys Setup

**Required:**
- **OpenAI API key** - Get at: https://platform.openai.com/api-keys

**Optional:**
- **Tally API key** - Get at: https://tally.so/help/api (only for form generation)
- **Twilio credentials** - Get at: https://www.twilio.com/console (only for SMS notifications)

## Usage

### Run as MCP Server

```bash
export OPENAI_API_KEY="sk-proj-..."
export TALLY_API_KEY="..."  # optional
event-planner-mcp
```

### Python Integration Example

```python
import asyncio
from agents import MCPServerStdio

async def main():
    async with MCPServerStdio(
        "event-planner-mcp",
        env={
            "OPENAI_API_KEY": "sk-proj-...",
            "TALLY_API_KEY": "...",
            "PLAN_EVENT_FORM_MODE": "skip"
        }
    ) as mcp:
        result = await mcp.call_tool("plan_event", {
            "event_details": {
                "event_name": "AI Summit",
                "event_type": "conference",
                "event_date": "2026-05-10",
                "location_preference": "Zurich",
                "guest_count": 300,
                "budget": "$50k"
            }
        })
        print(result)

asyncio.run(main())
```

## Available Tools

- `plan_event` - Plan an event (required: `event_name`, `event_type`)
- `list_event_outputs` - List generated files
- `read_event_output` - Read event files (ICS, PDF)

## Configuration

Set via environment variables:

| Variable | Required | Options | Default |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | Yes | - | - |
| `TALLY_API_KEY` | No | - | - |
| `PLAN_EVENT_FORM_MODE` | No | `skip`, `unsandboxed`, `sandboxed` | `skip` |
| `TWILIO_ACCOUNT_SID` | No | - | - |
| `TWILIO_AUTH_TOKEN` | No | - | - |
| `TWILIO_FROM_PHONE` | No | - | - |
| `TWILIO_TO_PHONE` | No | - | - |

## Development Setup

Clone and install:
```bash
git clone https://github.com/Adrien-Z/AI-Event-Planner-Agent.git
cd AI-Event-Planner-Agent
uv sync
```

Run CLI locally:
```bash
export OPENAI_API_KEY="sk-proj-..."
uv run python app.py
```

## Supported Event Types

Weddings, conferences, parties, galas, workshops, networking events, product launches, charity fundraisers, retreats, and more.

The system will then orchestrate multiple specialized agents to produce a comprehensive event plan with venue recommendations, catering options, speaker suggestions, timeline, budget breakdown, risk assessment, and more.


---

## For More Details

See `ARCHITECTURE.md` for detailed technical documentation.
