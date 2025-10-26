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

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Set up environment variables**:
   ```bash
   export OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

Run the AI Event Planner:

```bash
uv run python main.py
```

The system will prompt you for:
- Event type (wedding, conference, party, etc.)
- Event name
- Event date
- Location preference
- Budget range
- Guest count
- Special requirements

## Project Structure

```
AI-Event-Planner-Cursor/
├── main.py                   # Main entry point
├── event_planner.py          # Main application logic
├── specialized_agents.py     # Specialized agent definitions
├── coordinator_agent.py      # Coordinator agent logic
├── config.py                 # Configuration and event types
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## Specialized Agents

The system includes 7 core specialized agents with tools:

- **Venue Agent**: Venue selection, availability checking, logistics
- **Catering Agent**: Menu planning, vendor selection, dietary requirements
- **Speakers Agent**: Speaker recruitment, logistics, coordination
- **Programme Agent**: Event scheduling, session planning, timing
- **Communication Agent**: Marketing, invitations, attendee communication
- **Registration Agent**: Registration systems, check-in logistics
- **Sponsors Agent**: Sponsor relationships, revenue optimization

## Future Enhancements

The system is designed to integrate with MCP (Model Context Protocol) tools:

- **Email Integration**: Send invitation emails through MCP
- **Tally Forms**: Create registration/signup forms using Tally's MCP server
- **Calendar Integration**: Sync with calendar systems
- **Payment Processing**: Handle registration payments
- **CRM Integration**: Manage attendee relationships

## License

This project is licensed under the MIT License.
