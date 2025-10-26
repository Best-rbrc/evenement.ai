# AI Event Planner

An intelligent event planning system using OpenAI Agents SDK that coordinates specialized AI agents to handle different aspects of event planning. The system automatically determines which specialized agents are needed based on the event type and distributes tasks accordingly.

## Features

- **Intelligent Agent Selection**: Automatically determines which specialized agents are needed based on event type
- **Specialized Agents**: Dedicated agents for venue, catering, speakers, programme, communication, and more
- **Coordinator Agent**: Orchestrates all specialized agents to create comprehensive event plans
- **Event Type Support**: Works with weddings, conferences, parties, galas, workshops, and more
- **Future-Ready**: Designed to integrate with MCP tools for email invitations and Tally forms

## Supported Event Types

- **Weddings**: Venue, catering, decoration, photography, music, communication
- **Corporate Conferences**: Venue, catering, speakers, programme, communication, registration
- **Tech Conferences**: Venue, catering, speakers, programme, communication, registration, sponsors
- **Birthday Parties**: Venue, catering, decoration, entertainment, communication
- **Gala Dinners**: Venue, catering, decoration, entertainment, communication, seating
- **Workshops**: Venue, catering, speakers, programme, communication, materials
- **Networking Events**: Venue, catering, communication, registration, networking
- **Product Launches**: Venue, catering, speakers, programme, communication, media, demo
- **Charity Fundraisers**: Venue, catering, speakers, programme, communication, fundraising
- **Retreats**: Venue, catering, programme, communication, activities, accommodation

## Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/Adrien-Z/AI-Event-Planner-Agent.git
   cd AI-Event-Planner-Agent
   ```

2. **Install dependencies**:
   
   This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management. Install dependencies with:
   ```bash
   uv sync
   ```
   
   Alternatively, with pip:
   ```bash
   pip install -e .
   ```

3. **Set up environment variables**:
   
   Create a `.env` file in the project root or export the API key:
   ```bash
   export OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   **Important**: You must have a valid OpenAI API key. Get one at [platform.openai.com](https://platform.openai.com/api-keys).

## Usage

Run the AI Event Planner:

```bash
uv run python app.py
```

Or, if you installed with pip:

```bash
python app.py
```

The system will prompt you for:
- **Event type**: wedding, corporate conference, tech conference, birthday party, gala dinner, workshop, networking event, product launch, charity fundraiser, retreat, etc.
- **Event name**: Your event's name
- **Event date**: When the event takes place (e.g., 'March 15, 2024' or 'Q2 2024')
- **Location preference**: City or region (or 'flexible')
- **Budget range**: Approximate budget (e.g., '$5,000-$10,000', 'under $2,000', 'flexible')
- **Guest count**: Expected number of attendees (e.g., '50-100', '200+', 'flexible')
- **Special requirements**: Any special needs or themes (e.g., 'outdoor venue', 'vegetarian catering', 'accessibility needs', 'corporate theme')

The system will then orchestrate multiple specialized agents to produce a comprehensive event plan with venue recommendations, catering options, speaker suggestions, timeline, budget breakdown, risk assessment, and more.

## Project Structure

```
AI-Event-Planner-Agent/
├── app.py                       # Main CLI entry point
├── config.py                    # Configuration (AGENT_SPECIALIZATIONS)
├── pyproject.toml              # Project dependencies (uv/pip)
├── README.md                   # This file
├── ARCHITECTURE.md             # Detailed architecture documentation
├── custom_agents/              # Specialized agent factories
│   ├── __init__.py             # Package exports
│   ├── base.py                 # Agent creation mapping
│   ├── coordinator_agent.py    # Coordinator agent (orchestrates specialists)
│   ├── venue_agent.py          # Venue selection & logistics
│   ├── catering_agent.py       # Menu planning & vendor selection
│   ├── speaker_agent.py        # Speaker recruitment & coordination
│   ├── programme_agent.py      # Event scheduling & session planning
│   ├── communication_agent.py  # Marketing & invitations
│   ├── registration_agent.py   # Registration systems & check-in
│   ├── activities_agent.py     # Recreational activities planning
│   ├── entertainment_agent.py  # Entertainment booking & coordination
│   └── archive/                # Optional/archived agents
│       ├── decoration_agent.py
│       ├── photography_agent.py
│       ├── music_agent.py
│       ├── seating_agent.py
│       └── ...
├── workflows/                   # Workflow orchestration logic
│   ├── event_planning_workflow.py  # Main workflow entrypoint
│   └── plan_generation.py      # Iterative multi-round planning
└── tools/                       # Utility tools for agents
    ├── analysis_tools.py        # Event requirements & timeline analysis
    ├── budgeting.py             # Budget allocation & tracking
    ├── parsing.py               # Input parsing utilities
    └── risk.py                  # Risk assessment tools
```

## Specialized Agents

The system includes **8 core specialized agents** and several optional archived agents:

### Core Agents (always available)

- **Venue Agent**: Venue selection, availability checking, logistics planning
- **Catering Agent**: Menu planning, vendor selection, dietary requirements handling
- **Speaker Agent**: Speaker recruitment, logistics coordination, scheduling
- **Programme Agent**: Event scheduling, session planning, timing optimization
- **Communication Agent**: Marketing materials, invitations, attendee communication
- **Registration Agent**: Registration systems, check-in logistics, ticketing
- **Activities Agent**: Team-building activities, recreational planning
- **Entertainment Agent**: Entertainment booking, coordination, technical requirements

### Optional/Archived Agents

- **Decoration Agent**: Theming, visual design, venue styling
- **Photography Agent**: Photo/video coverage coordination
- **Music Agent**: Music selection, audio equipment
- **Seating Agent**: Seating arrangements, accessibility
- **Materials Agent**: Workshop materials, signage, swag
- **Networking Agent**: Networking sessions, facilitation
- **Media Agent**: Press relations, social media, live-streaming
- **Demo Agent**: Product demos, booth management
- **Sponsor Agent**: Sponsor relationships, revenue optimization
- **Accommodation Agent**: Hotel room blocks, logistics

## How It Works

### Architecture Overview

The system uses a **Coordinator Agent** pattern with specialized sub-agents:

1. **Workflow Orchestration** (`workflows/event_planning_workflow.py`)
   - Receives event details from the user
   - Infers which specialized agents are needed based on event type
   - Creates specialized agents and a coordinator agent
   - Delegates multi-round orchestration to `produce_actionable_plan`

2. **Iterative Plan Generation** (`workflows/plan_generation.py`)
   - Runs multiple rounds, one per specialized agent
   - Each agent receives full context (event details + prior agent outputs)
   - Coordinator synthesizes individual sections into a unified master plan
   - Handles clarifications, budget negotiations, and interdependencies

3. **Coordinator Agent** (`custom_agents/coordinator_agent.py`)
   - Central orchestrator that assigns budgets, answers questions, and approves proposals
   - Maintains a JSON log of decisions, allocations, and pending clarifications
   - Produces final unified JSON output with all event sections

4. **Specialized Agents** (`custom_agents/*.py`)
   - Domain experts for venue, catering, speakers, etc.
   - Use function tools (e.g., `WebSearchTool`, custom budget/analysis tools)
   - Produce structured JSON outputs for their respective sections

### Why Keep the Coordinator Agent?

The Coordinator Agent is **retained** because:
- It centralizes synthesis and handoffs (used by the existing `produce_actionable_plan` implementation)
- It manages budget allocation and negotiation across specialized agents
- It answers clarification questions from specialists without requiring user input
- It maintains a unified decision log and produces a single coherent master plan

This design matches the OpenAI Agents SDK's recommended patterns for multi-agent systems with handoffs and structured outputs.

## Future Enhancements

The system is designed to integrate with MCP (Model Context Protocol) tools:

- **Email Integration**: Send invitation emails through MCP
- **Tally Forms**: Create registration/signup forms using Tally's MCP server
- **Calendar Integration**: Sync with calendar systems
- **Payment Processing**: Handle registration payments
- **CRM Integration**: Manage attendee relationships

## Troubleshooting

### Missing API Key Error

If you see:
```
openai.OpenAIError: The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable
```

**Solution**: Set your OpenAI API key:
```bash
export OPENAI_API_KEY=sk-...your-key-here...
```

Or create a `.env` file:
```
OPENAI_API_KEY=sk-...your-key-here...
```

### Import Errors

If you see import errors like `ModuleNotFoundError: No module named 'agents'`:

**Solution**: Install dependencies using:
```bash
uv sync
```

Or with pip:
```bash
pip install 'openai-agents[viz]>=0.4.1' git+https://github.com/GuardiAgent/python-mcp-sandbox-openai-sdk.git
```

### Package Conflicts

If you encounter package conflicts (e.g., a conflicting `agents` package from TensorFlow):

**Solution**: Use a clean virtual environment or conda environment:
```bash
# Create a new conda environment
conda create -n event-planner python=3.11
conda activate event-planner

# Install dependencies
uv sync
```

## Development & Contributing

### Running Tests

(TODO: Add tests)

```bash
pytest tests/
```

### Code Structure

- `app.py`: CLI entrypoint that collects user input and calls the workflow
- `workflows/event_planning_workflow.py`: Main workflow entrypoint
- `workflows/plan_generation.py`: Async iterative orchestration logic
- `custom_agents/`: Specialized agent factory functions
- `tools/`: Utility functions and tools for agents

### Adding a New Agent

1. Create `custom_agents/your_agent.py` with a `create_your_agent()` factory function
2. Add the import and mapping in `custom_agents/base.py` (`AGENT_CREATORS` dict)
3. Add the agent to `custom_agents/__init__.py` exports
4. Update `config.py` with agent description (optional)
5. Update `workflows/event_planning_workflow.py` `infer_required_agents()` if needed

### Coordinator vs Orchestrator

**Decision**: The **Coordinator Agent is retained** because:
- The existing `produce_actionable_plan` implementation (from `workflows/plan_generation.py`) uses it for multi-round orchestration and synthesis
- It centralizes budget allocation, clarification handling, and final synthesis
- It follows OpenAI Agents SDK patterns for multi-agent systems with handoffs

The separate `Orchestrator` class (from the external `Event Planner/orchestrator` package) is **not needed** in this codebase because the workflow uses the SDK's `Runner.run_streamed` directly and the Coordinator agent handles synthesis.

## License

This project is licensed under the MIT License.
