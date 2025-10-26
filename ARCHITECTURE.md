# AI Event Planner Architecture

## Overview

The AI Event Planner is a sophisticated system that uses the OpenAI Agents SDK to coordinate multiple specialized AI agents for comprehensive event planning. The system intelligently determines which agents are needed based on the event type and distributes tasks accordingly.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Event Planner                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   Main App      │    │        Coordinator Agent        │ │
│  │ (event_planner) │◄──►│     (coordinator_agent)         │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│           │                        │                        │
│           │                        ▼                        │
│           │              ┌─────────────────┐                │
│           │              │ Specialized     │                │
│           │              │ Agents Pool     │                │
│           │              └─────────────────┘                │
│           │                        │                        │
│           │                        ▼                        │
│           │    ┌─────────┬─────────┬─────────┬─────────┐   │
│           │    │ Venue   │Catering │Speakers │Programme│   │
│           │    │ Agent   │ Agent   │ Agent   │ Agent   │   │
│           │    └─────────┴─────────┴─────────┴─────────┘   │
│           │    ┌─────────┬─────────┬─────────┬─────────┐   │
│           │    │Comm.    │Decor.   │Photo    │Music    │   │
│           │    │Agent    │Agent    │Agent    │Agent    │   │
│           │    └─────────┴─────────┴─────────┴─────────┘   │
│           │    ┌─────────┬─────────┬─────────┬─────────┐   │
│           │    │Reg.     │Sponsors │Seating  │Materials│   │
│           │    │Agent    │Agent    │Agent    │Agent    │   │
│           │    └─────────┴─────────┴─────────┴─────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Main Application (`event_planner.py`)

**Purpose**: Entry point and user interaction
**Responsibilities**:
- Collect event details from user
- Determine required specialized agents
- Initialize coordinator and specialized agents
- Orchestrate the planning session
- Present results to user

**Key Methods**:
- `collect_event_details()`: Interactive user input collection
- `determine_required_agents()`: Agent selection logic
- `initialize_agents()`: Agent instantiation
- `run_planning_session()`: Main planning orchestration

### 2. Coordinator Agent (`coordinator_agent.py`)

**Purpose**: Central orchestration and task distribution
**Responsibilities**:
- Analyze event requirements
- Distribute tasks to appropriate specialized agents
- Ensure comprehensive coverage
- Create cohesive timeline and action plan
- Identify challenges and solutions

**Key Functions**:
- `create_coordinator_agent()`: Agent creation with system prompt
- `coordinate_planning_session()`: Session orchestration
- `create_event_timeline()`: Timeline generation
- `create_budget_breakdown()`: Budget allocation
- `create_risk_assessment()`: Risk analysis

### 3. Specialized Agents (`specialized_agents.py`)

**Purpose**: Domain-specific expertise and planning
**Agent Types**:
- **Venue Agent**: Venue selection, logistics, setup
- **Catering Agent**: Menu planning, dietary requirements
- **Speakers Agent**: Speaker recruitment, contracts
- **Programme Agent**: Event scheduling, session planning
- **Communication Agent**: Marketing, invitations
- **Decoration Agent**: Theming, visual design
- **Photography Agent**: Photo coordination
- **Music Agent**: Music selection, audio equipment
- **Entertainment Agent**: Activity planning
- **Registration Agent**: Registration systems
- **Sponsors Agent**: Sponsor relationships
- **Seating Agent**: Seating arrangements
- **Materials Agent**: Workshop materials
- **Networking Agent**: Networking activities
- **Media Agent**: Press relations
- **Demo Agent**: Product demonstrations
- **Fundraising Agent**: Fundraising strategy
- **Activities Agent**: Recreational activities
- **Accommodation Agent**: Hotel booking

**Key Functions**:
- `create_specialized_agents()`: Agent factory
- Individual agent creators for each specialization

### 4. Configuration (`config.py`)

**Purpose**: System configuration and event type definitions
**Key Components**:
- `EVENT_TYPES`: Mapping of event types to required agents
- `AGENT_SPECIALIZATIONS`: Agent descriptions
- Environment variable management

## Event Type Classification

The system supports 10+ event types with intelligent agent selection:

| Event Type | Required Agents |
|------------|----------------|
| Wedding | venue, catering, decoration, photography, music, communication |
| Corporate Conference | venue, catering, speakers, programme, communication, registration |
| Tech Conference | venue, catering, speakers, programme, communication, registration, sponsors |
| Birthday Party | venue, catering, decoration, entertainment, communication |
| Gala Dinner | venue, catering, decoration, entertainment, communication, seating |
| Workshop | venue, catering, speakers, programme, communication, materials |
| Networking Event | venue, catering, communication, registration, networking |
| Product Launch | venue, catering, speakers, programme, communication, media, demo |
| Charity Fundraiser | venue, catering, speakers, programme, communication, fundraising |
| Retreat | venue, catering, programme, communication, activities, accommodation |

## Workflow

### 1. User Input Collection
```
User → Event Type Selection
     → Event Details (name, date, location, budget, guests)
     → Special Requirements
```

### 2. Agent Selection
```
Event Type → Agent Mapping → Required Agents List
```

### 3. Agent Initialization
```
Required Agents → Specialized Agent Creation → Agent Pool
```

### 4. Planning Session
```
Coordinator Agent → Task Distribution → Specialized Agents
                 → Results Aggregation → Comprehensive Plan
```

### 5. Result Presentation
```
Planning Results → Timeline → Budget → Risk Assessment → Action Items
```

## Future Enhancements

### MCP Integration
The system is designed for future MCP (Model Context Protocol) integration:

1. **Email Integration**: Send invitation emails through MCP
2. **Tally Forms**: Create registration/signup forms using Tally's MCP server
3. **Calendar Integration**: Sync with calendar systems
4. **Payment Processing**: Handle registration payments
5. **CRM Integration**: Manage attendee relationships

### Example MCP Integration
```python
# Future Tally form creation
tally_form = await create_tally_form({
    "title": f"{event_name} Registration",
    "fields": ["name", "email", "dietary_requirements", "accessibility_needs"]
})

# Future email sending
await send_invitation_email({
    "recipients": attendee_list,
    "subject": f"Invitation to {event_name}",
    "template": "conference_invitation",
    "registration_link": tally_form.url
})
```

## Scalability

### Horizontal Scaling
- Add new event types by extending `EVENT_TYPES`
- Add new specialized agents by creating new agent functions
- Modify agent selection logic in `determine_required_agents()`

### Vertical Scaling
- Enhance agent capabilities with more detailed instructions
- Add more sophisticated coordination logic
- Implement agent handoffs for complex workflows

### Integration Scaling
- Add new MCP servers for additional functionality
- Implement agent-to-agent communication
- Add real-time collaboration features

## Error Handling

### Agent Failures
- Graceful degradation when agents fail
- Fallback to generic planning
- Error reporting and logging

### User Input Validation
- Input validation and sanitization
- Default value assignment
- User-friendly error messages

### System Failures
- Retry mechanisms for API calls
- Offline mode capabilities
- Data persistence and recovery

## Performance Considerations

### Agent Efficiency
- Parallel agent execution where possible
- Caching of common responses
- Optimized prompt engineering

### Resource Management
- Memory usage optimization
- API rate limiting
- Cost optimization for OpenAI API calls

### Scalability
- Asynchronous processing
- Queue management for high-volume events
- Load balancing for multiple instances

## Security Considerations

### API Key Management
- Secure environment variable handling
- Key rotation capabilities
- Access logging and monitoring

### Data Privacy
- Event data encryption
- User data protection
- GDPR compliance considerations

### Agent Isolation
- Sandboxed agent execution
- Input validation and sanitization
- Output filtering and validation
