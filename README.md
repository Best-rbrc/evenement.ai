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

### Run the HTTP API (for the frontend)

```bash
uv run uvicorn server:app --reload --port 8000
```

The API loads your `.env` for `OPENAI_API_KEY` and exposes `POST /api/plan` that accepts the same inputs as the CLI (the frontend sends them in camelCase). CORS is open by default; set `ALLOWED_ORIGINS` to a comma-separated list if you want to restrict access.

### Run the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects `VITE_API_BASE_URL` to point to the API (defaults to `http://localhost:8000`). It keeps the loading view visible until the agents finish and displays the real workflow output.

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
│   ├── budgeting_agent.py     # Budget allocation & what-if scenarios
│   ├── form_agent.py          # Tally form creation (MCP integration)
│   ├── activities_agent.py     # Recreational activities planning
│   ├── entertainment_agent.py  # Entertainment booking & coordination
│   └── archive/                # Optional/archived agents
│       ├── decoration_agent.py
│       ├── photography_agent.py
│       ├── music_agent.py
│       ├── seating_agent.py
│       └── ...
├── workflows/                   # Workflow orchestration logic
│   └── event_planning_workflow.py  # Main 5-phase intelligent workflow
├── tools/                       # Utility tools for agents
│   ├── analysis_tools.py       # (Currently empty - coordinator uses handoffs)
│   └── report_generator.py    # Professional PDF report generation (NEW!)
└── event_outputs/               # Generated outputs (PDFs, ICS files, etc.)
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
- **Budgeting Agent**: Budget allocation, what-if scenario analysis, cost validation
- **Scheduling Agent**: Advanced constraint-based schedule optimization using Google OR-Tools (NEW!)

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

The system uses a **3-Phase Intelligent Workflow** with a Coordinator Agent pattern:

#### Phase 1: Strategic Planning
- Coordinator analyzes event requirements
- Decides which specialist agents are needed
- Determines optimal execution order
- Identifies special considerations and constraints

#### Phase 2: Specialist Execution
- Calls each specialist in the determined order
- Each specialist receives full context (event details + prior outputs)
- Collects structured outputs from all specialists
- Maintains coordination across interdependent areas (e.g., venue → catering)

#### Phase 3: Review, Refinement & Finalization
- Coordinator reviews all specialist outputs
- Identifies budget conflicts, gaps, or inconsistencies
- Can handoff to additional specialists as needed (even ones not initially called)
- Synthesizes final comprehensive event plan

#### Phase 4: Event Outputs
- Calendar agent generates .ics invite files
- Form agent creates registration forms
- **PDF report generator creates professional proposal** (NEW!)

#### Phase 5: Professional PDF Report
- Generates branded PDF proposal with executive summary
- Includes Gantt-style timeline visualization
- Budget breakdown tables with percentages
- Optimized schedule (if scheduling agent was used)
- Risk assessment matrix
- Action items checklist
- Professional formatting with custom color scheme

### Key Components

1. **Main Workflow** (`workflows/event_planning_workflow.py`)
   - `run_event_planning()`: Orchestrates the entire 3-phase process
   - Uses OpenAI Agents SDK's `Runner.run_sync()` for each phase
   - Handles handoffs between coordinator and specialists

2. **Coordinator Agent** (`custom_agents/coordinator_agent.py`)
   - Central orchestrator with strategic decision-making
   - Manages budget allocation and negotiations
   - Reviews outputs and identifies issues
   - Can dynamically call any specialist agent as needed
   - Produces final unified JSON output

3. **Specialized Agents** (`custom_agents/*.py`)
   - Domain experts for venue, catering, speakers, etc.
   - Use tools like `WebSearchTool` for real-world data
   - Produce structured JSON outputs for their sections
   - Examples: `venue_agent.py`, `catering_agent.py`, `speaker_agent.py`

4. **Agent Handoffs**
   - Coordinator can handoff to any specialist at any time
   - Specialists work with context from prior specialists
   - Enables iterative refinement and dynamic planning

### Budgeting Agent - What-If Scenario Planning

The **Budgeting Agent** is a specialized agent that provides comprehensive financial planning and analysis:

#### Core Capabilities

1. **Budget Allocation** (`calculate_budget_allocation`)
   - Distributes total budget across event categories
   - Uses priority-based allocation (high/medium/low)
   - Industry-standard percentage guidelines by category
   - Automatic contingency fund (10-15%)

2. **What-If Scenario Analysis** (`run_budget_scenario`)
   - Model impacts of budget changes before committing
   - Compare "what if we increase venue budget by $2000?" scenarios
   - Identify feasibility issues (over_budget, under_budget, feasible)
   - Provide clear recommendations for each scenario

3. **Multi-Scenario Comparison** (`compare_budget_scenarios`)
   - Evaluate multiple scenarios side-by-side
   - Score scenarios based on feasibility and contingency
   - Recommend optimal approach with reasoning

4. **Cost Validation** (`validate_category_costs`)
   - Check proposed costs against industry benchmarks
   - Per-person validation for scalable costs (venue, catering)
   - Per-event validation for fixed costs (speakers, photography)
   - Flag costs that are too high or suspiciously low

5. **Itemized Breakdowns** (`generate_cost_breakdown`)
   - Detailed line-item breakdowns by category
   - Venue: rental, setup, equipment, permits
   - Catering: food, beverages, staff, equipment
   - Speakers: honorarium, travel, accommodation

#### Integration in Workflow

The Budgeting Agent integrates seamlessly:
- **Early execution**: Creates baseline allocation before specialists provide estimates
- **Post-specialist validation**: Validates all specialist costs and runs scenarios
- **Conflict resolution**: When budget issues arise, automatically creates what-if scenarios
- **Final approval**: Ensures final plan meets budget constraints

Example workflow:
1. Coordinator selects required specialists
2. Budgeting Agent creates baseline allocation
3. Other specialists (venue, catering, etc.) provide recommendations within budget
4. Budgeting Agent validates all costs and runs what-if scenarios
5. If over budget, Budgeting Agent proposes alternative scenarios
6. Coordinator selects best scenario for final plan

### Scheduling Agent - Advanced Constraint Optimization

The **Scheduling Agent** uses **Google OR-Tools** constraint programming to optimize complex event schedules:

#### Core Capabilities

1. **Constraint-Based Optimization** (`optimize_schedule`)
   - **No room conflicts**: Prevents double-booking of rooms
   - **No speaker conflicts**: Ensures speakers aren't scheduled in two places at once
   - **Capacity matching**: Assigns sessions to rooms with adequate capacity
   - **Travel time buffers**: Adds time between sessions for speaker movement
   - **Break enforcement**: Respects lunch breaks and mandatory pauses
   - **Compact scheduling**: Minimizes total event duration

2. **Conflict Detection & Resolution**
   - Identifies infeasible schedules and explains why
   - Provides actionable suggestions (add rooms, reduce sessions, extend hours)
   - Scores schedules by feasibility and efficiency

3. **What-If Analysis** (`analyze_schedule_conflicts`)
   - Test adding new sessions without making changes
   - Detect conflicts before committing
   - Get recommendations for resolution

4. **Optimization Objectives**
   - Minimize total event duration (compact schedule)
   - Maximize room utilization
   - Balance session distribution
   - Respect speaker preferences

#### Integration in Workflow

The Scheduling Agent runs after Programme and Speakers agents:
1. Extracts sessions from Programme Agent output
2. Identifies rooms from Venue Agent output
3. Determines speaker availability and travel requirements
4. Applies constraints (event hours, breaks, capacity)
5. Uses CP-SAT solver to find optimal schedule
6. Returns optimized schedule with metrics or conflict explanations

Example input:
```json
{
  "sessions": [{"id": 1, "name": "Keynote", "duration": 60, "speaker": "Dr. Weber", "expected_attendees": 100}],
  "rooms": [{"id": 1, "name": "Main Hall", "capacity": 200}],
  "speakers": [{"id": "Dr. Weber", "travel_time_minutes": 30}],
  "constraints": {"event_start": "09:00", "event_end": "18:00", "lunch_break": "12:00-13:00"}
}
```

### Why the Coordinator Agent?

The Coordinator Agent is essential because it:
- Makes strategic decisions (which agents, what order)
- Orchestrates budget management via Budgeting Agent
- Coordinates constraint optimization via Scheduling Agent
- Reviews and synthesizes all specialist outputs
- Handles iterative refinement (can call agents multiple times)
- Produces a coherent final plan from distributed specialist work

This design follows OpenAI Agents SDK best practices for multi-agent orchestration with handoffs.

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
5. The workflow will automatically make it available to the coordinator

### Architecture Decisions

**Coordinator Agent**: The Coordinator Agent is retained and essential because:
- Makes strategic decisions about which specialists to use and in what order
- Manages budget allocation and negotiation across specialists
- Reviews outputs, identifies gaps/conflicts, and iteratively refines
- Can dynamically handoff to any specialist (even ones not initially called)
- Synthesizes all specialist outputs into a cohesive final plan
- Follows OpenAI Agents SDK patterns for multi-agent orchestration

**No Separate Orchestrator Class**: The workflow uses OpenAI SDK's `Runner` directly with the Coordinator agent handling synthesis through handoffs.

## License

This project is licensed under the MIT License.
