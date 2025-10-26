"""Coordinator agent that distributes work to specialized agents."""
from typing import Dict, List, Any
from agents import Agent
from config import AGENT_SPECIALIZATIONS
from tools.analysis_tools import analyze_event_requirements, create_event_timeline, coordinate_agent_tasks



def create_coordinator_agent(event_details: Dict[str, Any], required_agents: List[str], specialized_agents: Dict[str, Agent]) -> Agent:
    """Create a coordinator agent that manages and distributes work to specialized agents."""
    
    # Create handoffs list from specialized agents
    handoffs = list(specialized_agents.values())
    
    # Create a comprehensive system prompt for the coordinator
    # NOTE: this prompt is intentionally prescriptive so the coordinator returns a finished,
    # actionable plan (venue, catering, schedule, speakers, contact templates, Tally form schema,
    # and MCP-ready draft emails) without stopping to ask follow-up questions.
    system_prompt = f"""
You are the Event Planning Coordinator responsible for delivering a complete, actionable event
plan for "{event_details['event_name']}", a {event_details['event_type']} event. Use the available
specialized agents to research and fill in details, but do not stop the workflow asking for more
user input — produce a finished plan the user can act on.

Event Details
-------------
- Name: {event_details['event_name']}
- Type: {event_details['event_type']}
- Date: {event_details['event_date']}
- Location preference: {event_details['location_preference']}
- Budget: {event_details['budget_range']}
- Guest count: {event_details['guest_count']}
- Special requirements: {event_details['special_requirements']}

Available Specialized Agents:
{', '.join([f"{agent}: {AGENT_SPECIALIZATIONS.get(agent, 'Specialized planning')}" for agent in required_agents])}

Deliverables (required, produce each as explicit, actionable outputs):
1) Primary venue recommendation (choose 1 primary + 2 backups): include name, city, estimated cost,
   why it fits, contact person or placeholder contact email, and a short venue booking email template (MCP-ready).
2) Primary catering partner (choose 1 primary + 1 backup): include caterer name, sample menu for the guest count,
   estimated per-person cost, and a catering inquiry email (MCP-ready) to request a quote.
3) Full event schedule (hour-by-hour for the event day plus pre-event milestones) with assigned responsible agent
   for each item. For sessions that need speakers, list suggested speaker names/roles and a speaker outreach email draft.
4) Speakers list and suggested talk titles/abstracts (fake/sample speakers are acceptable if real contact info
   is not available). Provide speaker outreach emails (MCP-ready) and a fallback plan if speaker cancels.
5) Registration/signup form prepared as a Tally-like form schema (provide field list, field types, validation rules,
   privacy settings, and a JSON payload that could be used by an MCP Tally server to create the form).
6) Invitation email (subject, plain-text and HTML body) ready to send via MCP, plus reminder and thank-you templates.
7) Vendor contracts/checklist: short checklist items and deadlines for venue, catering, AV, speakers, and accommodation.
8) Final budget summary allocating amounts to venue, catering, speakers, programme, and communication.

Output format requirements:
- Produce a clear final section titled "FINAL DELIVERABLES" that contains the completed items 1–8.
- For every email/template and the Tally form, include a JSON object labeled as "MCP_PAYLOAD" showing the
  fields and a short explanation of how to send this via an MCP tool (what endpoints/fields to include).
- Do not ask the user more questions — assume reasonable defaults where necessary and note any assumptions.

Prioritize actionability: each recommended venue/caterer/speaker should include the exact next steps and a copy-pastable
email or MCP payload someone on the event team can send.
"""
    
    return Agent(
        name="Event Planning Coordinator",
        instructions=system_prompt,
        tools=[analyze_event_requirements, create_event_timeline, coordinate_agent_tasks],
        handoffs=handoffs
    )
