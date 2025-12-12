# AI Event Planner Agent

An intelligent, multi-agent event planning system powered by OpenAI Agents SDK that orchestrates specialized AI agents to create comprehensive, actionable event plans. The system provides both a web interface and MCP (Model Context Protocol) server integration for seamless integration with AI assistants and development tools.

## Overview

The AI Event Planner Agent is a sophisticated event planning system that leverages multiple specialized AI agents to handle different aspects of event planning. The system intelligently coordinates agents for venue selection, catering, budgeting, scheduling, speaker management, and more, producing detailed plans with timelines, budgets, risk assessments, and actionable items.

## Key Features

### Multi-Agent Orchestration
- Intelligent agent selection based on event type
- Coordinated workflow with specialized domain agents
- Automatic task distribution and result synthesis

### Comprehensive Planning
- Venue recommendations with logistics analysis
- Catering options with dietary accommodations
- Budget allocation and what-if scenario analysis
- Schedule optimization with conflict resolution
- Speaker recommendations and management
- Programme planning and session flow
- Communication and marketing strategies
- Activity and entertainment planning

### Output Generation
- PDF event proposal reports
- ICS calendar files for event import
- Registration forms via Tally integration
- Custom logo generation
- SMS notifications (optional)

### Integration Options
- Web-based interface with React frontend
- MCP server for Claude Desktop, Cursor IDE, and other MCP clients
- RESTful API for programmatic access
- Command-line interface

### Plan Refinement
- Chat-based plan updates
- Incremental agent re-execution
- Change tracking and coordination

## Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- (Optional) Tally API key for form generation
- (Optional) Twilio credentials for SMS notifications

### Install from Source

```bash
git clone https://github.com/Adrien-Z/AI-Event-Planner-Agent.git
cd AI-Event-Planner-Agent
uv sync  # or: pip install -e .
```

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional - Form generation
TALLY_API_KEY=your-tally-api-key
PLAN_EVENT_FORM_MODE=skip  # Options: skip, unsandboxed, sandboxed

# Optional - SMS notifications
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_PHONE=+1234567890
TWILIO_TO_PHONE=+0987654321
```

## Usage

### Web Interface

Start the development server:

```bash
export OPENAI_API_KEY="sk-proj-..."
uv run python server.py
```

Access the interface at `http://localhost:8000`

### MCP Server

For integration with Claude Desktop, Cursor IDE, or other MCP clients:

```bash
export OPENAI_API_KEY="sk-proj-..."
event-planner-mcp
```

See [MCP_USAGE.md](MCP_USAGE.md) for detailed MCP integration instructions.

### Command Line Interface

```bash
export OPENAI_API_KEY="sk-proj-..."
uv run python cli.py
```

### Programmatic API

```python
from workflows.event_planning_workflow import run_event_planning

event_details = {
    "event_name": "Tech Conference 2024",
    "event_type": "conference",
    "event_date": "2024-06-15",
    "location_preference": "San Francisco, CA",
    "budget_range": "$50,000-$75,000",
    "guest_count": "200-300",
    "special_requirements": "Accessible venue, vegetarian options"
}

result = run_event_planning(event_details)
```

## Supported Event Types

The system supports a wide range of event types with intelligent agent selection:

- Conferences (corporate, tech, academic)
- Weddings and celebrations
- Workshops and training sessions
- Networking events
- Product launches
- Charity fundraisers
- Corporate galas
- Retreats and team building
- And more

## System Architecture

The system follows a multi-phase workflow:

1. **Planning Phase**: Coordinator agent analyzes requirements and determines necessary specialists
2. **Execution Phase**: Specialized agents work in parallel to create domain-specific recommendations
3. **Finalization Phase**: Coordinator synthesizes all outputs into a comprehensive plan
4. **Output Generation**: Calendar files, PDF reports, forms, and logos are created

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Available Agents

### Core Agents
- **Coordinator Agent**: Orchestrates planning workflow and synthesizes results
- **Venue Agent**: Venue selection, logistics, and setup recommendations
- **Catering Agent**: Menu planning and dietary accommodations
- **Budgeting Agent**: Budget allocation and scenario analysis
- **Scheduling Agent**: Schedule optimization with constraint resolution
- **Programme Agent**: Event structure and session flow
- **Speaker Agent**: Speaker recommendations and management
- **Communication Agent**: Marketing and communication strategies
- **Entertainment Agent**: Entertainment and activity planning
- **Activities Agent**: Activity recommendations and logistics

### Output Agents
- **Calendar Agent**: ICS file generation
- **Form Agent**: Registration form creation via Tally
- **Logo Agent**: Custom logo generation

## API Endpoints

### Web Server Endpoints

- `POST /api/plan` - Create a new event plan
- `POST /api/refine-plan` - Refine an existing plan based on chat input
- `GET /api/progress` - Get current planning progress
- `POST /api/voice-to-form` - Convert voice input to form data

### MCP Server Tools

- `plan_event` - Plan a complete event
- `list_event_outputs` - List generated files
- `read_event_output` - Read file contents

## Output Structure

Each event plan includes:

- **Executive Summary**: High-level overview
- **Timeline**: Phased timeline with tasks and deadlines
- **Schedule**: Optimized event schedule with sessions
- **Budget**: Detailed budget breakdown by category
- **Recommendations**: Complete specialist outputs
- **Risks**: Identified risks with mitigation strategies
- **Action Items**: Prioritized tasks with owners and deadlines
- **Assumptions**: Documented planning assumptions

## Configuration Options

### Form Creation Mode

- `skip`: No form creation (fastest, default)
- `unsandboxed`: Direct Tally API integration (requires TALLY_API_KEY)
- `sandboxed`: Docker-based sandboxed execution (requires Docker)

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | Yes | OpenAI API key | - |
| `TALLY_API_KEY` | No | Tally API key for forms | - |
| `PLAN_EVENT_FORM_MODE` | No | Form creation mode | `skip` |
| `TWILIO_ACCOUNT_SID` | No | Twilio account SID | - |
| `TWILIO_AUTH_TOKEN` | No | Twilio auth token | - |
| `TWILIO_FROM_PHONE` | No | Twilio sender phone | - |
| `TWILIO_TO_PHONE` | No | Twilio recipient phone | - |

## Development

### Project Structure

```
AI-Event-Planner-Agent/
├── custom_agents/          # Specialized AI agents
├── custom_mcp_servers/     # MCP server implementations
├── workflows/              # Core workflow logic
├── tools/                  # Utility tools
├── frontend/               # React web interface
├── server.py               # FastAPI web server
├── cli.py                  # Command-line interface
└── tests/                  # Test suite
```

### Running Tests

```bash
uv run pytest tests/
```

### Development Dependencies

The project uses:
- OpenAI Agents SDK for agent orchestration
- FastAPI for web server
- React + TypeScript for frontend
- FastMCP for MCP server
- Pydantic for data validation
- OR-Tools for scheduling optimization

## Documentation

- [MCP_USAGE.md](MCP_USAGE.md) - MCP server integration guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design

## License

MIT License

