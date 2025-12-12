# AI Event Planner Architecture

## Overview

The AI Event Planner is a sophisticated multi-agent system built on the OpenAI Agents SDK that coordinates specialized AI agents to create comprehensive event plans. The architecture follows a three-phase workflow pattern with intelligent agent selection, parallel execution, and result synthesis.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI Event Planner System                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐         ┌──────────────────────────────┐   │
│  │   Frontend   │         │      Web Server (FastAPI)     │   │
│  │   (React)    │◄────────►│         (server.py)          │   │
│  └──────────────┘         └──────────────────────────────┘   │
│         │                              │                       │
│         │                              │                       │
│         │                    ┌─────────▼──────────┐           │
│         │                    │  Workflow Engine    │           │
│         │                    │ (event_planning_    │           │
│         │                    │   workflow.py)      │           │
│         │                    └─────────┬──────────┘           │
│         │                              │                       │
│         │                    ┌─────────▼──────────┐           │
│         │                    │ Coordinator Agent │           │
│         │                    │  (3 Phases)      │           │
│         │                    └─────────┬──────────┘           │
│         │                              │                       │
│         │                    ┌─────────▼──────────┐           │
│         │                    │ Specialized Agents │           │
│         │                    │      Pool          │           │
│         │                    └─────────┬──────────┘           │
│         │                              │                       │
│         │         ┌────────────────────┼────────────────────┐ │
│         │         │                    │                    │ │
│         │  ┌──────▼──────┐    ┌───────▼──────┐    ┌───────▼──┐│
│         │  │   Venue     │    │  Catering    │    │ Budgeting││
│         │  │   Agent     │    │   Agent      │    │  Agent   ││
│         │  └─────────────┘    └──────────────┘    └──────────┘│
│         │  ┌─────────────┐    ┌──────────────┐    ┌──────────┐│
│         │  │ Scheduling  │    │  Programme   │    │ Speakers ││
│         │  │   Agent     │    │   Agent      │    │  Agent   ││
│         │  └─────────────┘    └──────────────┘    └──────────┘│
│         │  ┌─────────────┐    ┌──────────────┐    ┌──────────┐│
│         │  │Communication│    │Entertainment │    │Activities││
│         │  │   Agent     │    │   Agent      │    │  Agent   ││
│         │  └─────────────┘    └──────────────┘    └──────────┘│
│         │  ┌─────────────┐    ┌──────────────┐               │
│         │  │  Calendar   │    │    Form      │               │
│         │  │   Agent     │    │   Agent      │               │
│         │  └─────────────┘    └──────────────┘               │
│         │  ┌─────────────┐                                    │
│         │  │   Logo      │                                    │
│         │  │   Agent     │                                    │
│         │  └─────────────┘                                    │
│         │                                                      │
│  ┌──────▼──────────────────────────────────────────────────┐ │
│  │              MCP Server (FastMCP)                       │ │
│  │         (custom_mcp_servers/fastmcp_server.py)          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Workflow Engine

**Location**: `workflows/event_planning_workflow.py`

The workflow engine orchestrates the entire event planning process through four distinct phases.

#### Phase 1: Planning and Analysis

The planning coordinator analyzes event requirements and determines which specialized agents are needed based on:
- Event type (conference, wedding, workshop, etc.)
- Event complexity
- User requirements
- Budget constraints

**Output**: Planning analysis with required agents list and execution rationale.

#### Phase 2: Specialized Agent Execution

Specialized agents execute in parallel (or sequentially based on dependencies) to create domain-specific recommendations. Each agent:
- Receives event context and requirements
- Accesses relevant specialist outputs for coordination
- Produces structured output using Pydantic schemas
- Returns validated recommendations

**Agents Executed**:
- Venue Agent
- Catering Agent
- Budgeting Agent
- Programme Agent
- Speaker Agent
- Scheduling Agent (for multi-session events)
- Communication Agent
- Entertainment Agent
- Activities Agent

#### Phase 3: Finalization and Synthesis

The finalization coordinator:
- Reviews all specialist outputs
- Validates budget constraints
- Resolves conflicts between recommendations
- Synthesizes a comprehensive final plan
- Generates timeline, schedule, budget, risks, and action items

#### Phase 4: Output Generation

Post-processing agents create deliverable outputs:
- Calendar Agent: ICS file generation
- Form Agent: Registration form via Tally MCP
- Logo Agent: Custom logo generation
- PDF Generator: Comprehensive event proposal report

### 2. Coordinator Agent

**Location**: `custom_agents/coordinator_agent.py`

The coordinator agent operates in three distinct modes:

#### Planning Coordinator

- Analyzes event requirements
- Determines required specialist agents
- Creates execution order rationale
- Identifies special considerations

#### Main Coordinator

- Orchestrates agent handoffs
- Manages task distribution
- Coordinates multi-agent workflows
- Handles agent-to-agent communication

#### Finalization Coordinator

- Synthesizes all specialist outputs
- Creates comprehensive final plan
- Validates consistency across recommendations
- Generates executive summary, timeline, budget, risks, and action items

**Key Features**:
- Handoff capability to all specialized agents
- Context-aware decision making
- Budget validation and conflict resolution
- Schedule optimization coordination

### 3. Specialized Agents

**Location**: `custom_agents/`

Each specialized agent is a domain expert with specific responsibilities:

#### Venue Agent
- Venue research and recommendations
- Capacity and logistics analysis
- Cost estimation
- Availability assessment
- Backup venue options

#### Catering Agent
- Menu planning and recommendations
- Dietary accommodation planning
- Budget estimation per person
- Timeline and logistics
- Vendor coordination notes

#### Budgeting Agent
- Budget allocation across categories
- What-if scenario analysis
- Budget status monitoring (within/over/at limit)
- Category breakdowns
- Scenario recommendations

#### Scheduling Agent
- Multi-session schedule optimization
- Constraint-based scheduling using OR-Tools
- Conflict detection and resolution
- Room utilization optimization
- Time slot optimization

#### Programme Agent
- Event structure and flow
- Session planning
- Break and networking coordination
- Technical requirements
- Contingency planning

#### Speaker Agent
- Speaker recommendations
- Honorarium budgeting
- Logistics coordination
- Backup speaker plans
- Technical dependencies

#### Communication Agent
- Marketing channel selection
- Key message development
- Communication timeline
- Budget allocation for marketing
- Multi-channel strategy

#### Entertainment Agent
- Entertainment option recommendations
- Package recommendations
- Budget estimation
- Technical requirements
- Backup plans

#### Activities Agent
- Activity recommendations
- Logistics planning
- Budget estimation
- Safety considerations
- Success metrics

### 4. Output Agents

#### Calendar Agent
- ICS file generation
- Event import instructions
- Timing details

#### Form Agent
- Tally form creation via MCP
- Registration form configuration
- Form URL generation

#### Logo Agent
- Custom logo generation
- Design rationale
- Format optimization

### 5. Data Schemas

**Location**: `workflows/pydantic_schemas.py`

All agent outputs use Pydantic schemas for validation and structure:

- `PlanningOutput`: Planning phase results
- `VenueOutput`: Venue recommendations
- `CateringOutput`: Catering recommendations
- `BudgetingOutput`: Budget analysis
- `ProgrammeOutput`: Programme structure
- `SpeakersOutput`: Speaker recommendations
- `SchedulingOutput`: Optimized schedule
- `CommunicationOutput`: Communication plan
- `EntertainmentOutput`: Entertainment recommendations
- `ActivitiesOutput`: Activity planning
- `FinalPlanOutput`: Complete synthesized plan

### 6. Workflow Utilities

**Location**: `workflows/workflow_utils.py`

Utility functions for:
- Agent execution with retry logic
- Progress tracking
- Error handling
- Result validation

### 7. Plan Refinement

**Location**: `workflows/plan_refinement.py`

Incremental plan update system:
- Chat-based refinement requests
- Intelligent agent selection from user input
- Incremental agent re-execution
- Change tracking
- Result merging

## Workflow Execution

### Standard Workflow

```
1. User Input → Event Details Collection
2. Planning Phase → Coordinator analyzes requirements
3. Agent Selection → Required agents determined
4. Parallel Execution → Specialized agents run
5. Finalization → Coordinator synthesizes results
6. Output Generation → Calendar, PDF, Forms, Logo
7. Result Return → Complete plan with all outputs
```

### Refinement Workflow

```
1. User Chat Message → Refinement request
2. Agent Inference → Determine which agents to update
3. Selective Re-execution → Only affected agents run
4. Budget Validation → Budgeting agent validates changes
5. Plan Regeneration → Final plan updated with changes
6. Change Summary → List of modified sections
```

## Integration Points

### MCP Integration

**Location**: `custom_mcp_servers/`

The system provides MCP server integration via FastMCP:

- **FastMCP Server**: Main MCP server exposing planning tools
- **Tally MCP Server**: Form creation integration
- **Calendar MCP**: Calendar file generation

### Web Server

**Location**: `server.py`

FastAPI-based web server providing:
- RESTful API endpoints
- WebSocket support for progress tracking
- Frontend serving
- Plan refinement via chat

### Frontend

**Location**: `frontend/`

React + TypeScript frontend with:
- Event form input
- Real-time progress tracking
- Results visualization
- Chat-based refinement
- Export capabilities

## Data Flow

### Input Processing

```
User Input → Event Details Dict → Workflow Engine → Coordinator
```

### Agent Execution

```
Coordinator → Agent Selection → Specialized Agents → Structured Outputs
```

### Result Synthesis

```
Structured Outputs → Finalization Coordinator → Final Plan → Output Generation
```

### Output Delivery

```
Final Plan → PDF/ICS/Form/Logo → User/Frontend/MCP Client
```

## Agent Communication

### Handoff Mechanism

Agents communicate through the coordinator using handoffs:
- Coordinator can handoff to any specialized agent
- Agents receive context from previous agents
- Coordinator aggregates results

### Context Sharing

- Event details shared with all agents
- Specialist outputs available for coordination
- Budget constraints propagated
- Schedule constraints shared

## Scheduling Optimization

The scheduling agent uses OR-Tools for constraint-based optimization:

- **Variables**: Session time slots, room assignments
- **Constraints**: Room capacity, speaker availability, time conflicts
- **Objectives**: Maximize room utilization, minimize conflicts
- **Output**: Optimized schedule with metrics

## Error Handling

### Agent Failures

- Graceful degradation when agents fail
- Fallback to basic recommendations
- Error logging and reporting
- User notification of issues

### Validation

- Pydantic schema validation for all outputs
- Input validation at API boundaries
- Type checking throughout
- Error messages for invalid inputs

### Retry Logic

- Automatic retries for transient failures
- Exponential backoff for API calls
- Timeout handling
- Circuit breaker patterns

## Performance Considerations

### Parallel Execution

Specialized agents execute in parallel where possible to reduce total execution time.

### Caching

- Agent outputs cached during workflow
- Reused for finalization phase
- Shared across refinement requests

### Optimization

- Scheduling agent uses optimization algorithms
- Budget agent uses scenario analysis
- Efficient data structures throughout

## Security

### API Key Management

- Environment variable storage
- No hardcoded credentials
- Secure key handling

### Input Validation

- All inputs validated
- SQL injection prevention
- XSS protection in frontend
- Path traversal prevention

### Output Sanitization

- Output validation before delivery
- Safe file handling
- Secure file paths

## Testing

**Location**: `tests/`

Test suite includes:
- Unit tests for agents
- Integration tests for workflows
- MCP client tests
- Schema validation tests
- End-to-end workflow tests

## Extensibility

### Adding New Agents

1. Create agent file in `custom_agents/`
2. Implement agent creation function
3. Add to agent factory in `base.py`
4. Create Pydantic schema in `pydantic_schemas.py`
5. Update coordinator prompts if needed

### Adding New Event Types

1. Update event type mapping in workflow
2. Define required agents for new type
3. Update prompts if needed
4. Test with new event type

### Adding New Output Formats

1. Create output agent
2. Integrate into workflow Phase 4
3. Update result structure
4. Add frontend support if needed

## Future Enhancements

### Planned Features

- Multi-language support
- Integration with more calendar systems
- Advanced analytics and reporting
- Collaborative planning features
- Real-time collaboration
- Mobile application
- API rate limiting and quotas
- Advanced caching strategies

### Integration Opportunities

- CRM systems
- Payment processing
- Email marketing platforms
- Social media integration
- Video conferencing platforms
- Project management tools
