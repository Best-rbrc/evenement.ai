"""Coordinator agent that distributes work to specialized agents."""
from typing import Dict, List, Any
from agents import Agent, Runner, function_tool
from config import AGENT_SPECIALIZATIONS
import json
import re
import random


@function_tool
def analyze_event_requirements(event_name: str, event_type: str, guest_count: str) -> str:
    """Analyze event requirements and determine planning needs."""
    return f"Analyzed requirements for {event_name}: {event_type} event with {guest_count} guests"

@function_tool
def create_event_timeline(event_name: str, num_agents: int) -> str:
    """Create a comprehensive timeline for the event."""
    return f"Created timeline for {event_name} with {num_agents} specialized areas"

@function_tool
def coordinate_agent_tasks(event_name: str, agent_type: str) -> str:
    """Coordinate specific tasks for a specialized agent."""
    return f"Coordinated {agent_type} tasks for {event_name}"

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


async def coordinate_planning_session(coordinator: Agent, event_details: Dict[str, Any], required_agents: List[str], specialized_agents: Dict[str, Agent]) -> str:
    """Coordinate a planning session with all specialized agents."""
    
    # Create detailed planning prompt
    planning_prompt = f"""
    Please create a comprehensive event plan for "{event_details['event_name']}" by coordinating with the following specialized agents:
    
    Required Agents: {', '.join(required_agents)}
    
    For each agent, provide:
    1. Specific tasks and responsibilities
    2. Key deliverables and requirements
    3. Timeline and deadlines
    4. Budget considerations
    5. Dependencies and coordination needs
    6. Potential challenges and solutions
    
    Create an overall event timeline that shows:
    - Pre-event planning phases
    - Event day timeline
    - Post-event follow-up
    
    Ensure all aspects of the event are covered and that there are no conflicts or gaps in the planning.
    """
    
    try:
        result = await Runner.run_async(coordinator, planning_prompt)
        return result.final_output
    except Exception as e:
        return f"Error during coordination: {e}"


def create_event_timeline_from_details(event_details: Dict[str, Any], required_agents: List[str]) -> Dict[str, Any]:
    """Create a comprehensive event timeline based on event details and required agents.

    Renamed to avoid colliding with the @function_tool `create_event_timeline` defined
    earlier in this module (which is intended to be exposed as a FunctionTool)."""
    
    timeline = {
        "pre_event": {
            "12_weeks_before": [],
            "8_weeks_before": [],
            "4_weeks_before": [],
            "2_weeks_before": [],
            "1_week_before": [],
            "3_days_before": [],
            "1_day_before": []
        },
        "event_day": {
            "morning_setup": [],
            "afternoon_prep": [],
            "evening_event": [],
            "cleanup": []
        },
        "post_event": {
            "immediate": [],
            "1_week_after": [],
            "1_month_after": []
        }
    }
    
    # Add timeline items based on required agents
    if "venue" in required_agents:
        timeline["pre_event"]["12_weeks_before"].append("Venue selection and booking")
        timeline["pre_event"]["8_weeks_before"].append("Venue contract finalization")
        timeline["pre_event"]["1_week_before"].append("Final venue walkthrough")
        timeline["event_day"]["morning_setup"].append("Venue setup and preparation")
    
    if "catering" in required_agents:
        timeline["pre_event"]["8_weeks_before"].append("Catering vendor selection")
        timeline["pre_event"]["4_weeks_before"].append("Menu finalization")
        timeline["pre_event"]["1_week_before"].append("Final headcount confirmation")
        timeline["event_day"]["afternoon_prep"].append("Catering setup")
    
    if "speakers" in required_agents:
        timeline["pre_event"]["12_weeks_before"].append("Speaker recruitment")
        timeline["pre_event"]["8_weeks_before"].append("Speaker contracts")
        timeline["pre_event"]["2_weeks_before"].append("Speaker briefings")
        timeline["event_day"]["morning_setup"].append("Speaker setup and testing")
    
    if "communication" in required_agents:
        timeline["pre_event"]["12_weeks_before"].append("Save the date announcements")
        timeline["pre_event"]["8_weeks_before"].append("Invitation design and distribution")
        timeline["pre_event"]["2_weeks_before"].append("Final reminders")
        timeline["post_event"]["immediate"].append("Thank you messages")
    
    if "programme" in required_agents:
        timeline["pre_event"]["8_weeks_before"].append("Programme design")
        timeline["pre_event"]["4_weeks_before"].append("Speaker coordination")
        timeline["pre_event"]["1_week_before"].append("Final programme review")
        timeline["event_day"]["evening_event"].append("Programme execution")
    
    return timeline


def create_budget_breakdown(event_details: Dict[str, Any], required_agents: List[str]) -> Dict[str, Any]:
    """Create a budget breakdown based on event details and required agents."""
    
    budget_categories = {}
    
    # Base budget allocation percentages by event type
    event_type = event_details.get("event_type", "").lower()
    
    if "wedding" in event_type:
        budget_categories = {
            "venue": 0.40,
            "catering": 0.30,
            "decoration": 0.15,
            "photography": 0.10,
            "music": 0.05
        }
    elif "conference" in event_type or "corporate" in event_type:
        budget_categories = {
            "venue": 0.35,
            "catering": 0.25,
            "speakers": 0.20,
            "communication": 0.10,
            "programme": 0.10
        }
    elif "tech" in event_type:
        budget_categories = {
            "venue": 0.30,
            "catering": 0.20,
            "speakers": 0.25,
            "programme": 0.15,
            "communication": 0.10
        }
    else:
        # Default allocation
        budget_categories = {
            "venue": 0.30,
            "catering": 0.25,
            "communication": 0.20,
            "programme": 0.15,
            "other": 0.10
        }
    
    # Adjust based on available agents
    available_agents = [agent for agent in required_agents if agent in budget_categories]
    
    if available_agents:
        # Redistribute budget among available agents
        total_allocation = sum(budget_categories.get(agent, 0) for agent in available_agents)
        if total_allocation > 0:
            for agent in available_agents:
                budget_categories[agent] = budget_categories.get(agent, 0) / total_allocation
    
    return budget_categories


def create_risk_assessment(event_details: Dict[str, Any], required_agents: List[str]) -> Dict[str, List[str]]:
    """Create a risk assessment based on event details and required agents."""
    
    risks = {
        "high_risk": [],
        "medium_risk": [],
        "low_risk": []
    }
    
    # Common risks for all events
    risks["high_risk"].extend([
        "Weather issues (for outdoor events)",
        "Venue availability changes",
        "Key speaker cancellations"
    ])
    
    risks["medium_risk"].extend([
        "Catering delivery issues",
        "Technical equipment failures",
        "Transportation delays"
    ])
    
    risks["low_risk"].extend([
        "Minor schedule adjustments",
        "Small attendance variations",
        "Decoration timing issues"
    ])
    
    # Event-specific risks
    event_type = event_details.get("event_type", "").lower()
    
    if "wedding" in event_type:
        risks["high_risk"].append("Vendor no-shows")
        risks["medium_risk"].append("Guest count changes")
    
    elif "conference" in event_type:
        risks["high_risk"].append("Speaker cancellations")
        risks["medium_risk"].append("Registration system issues")
    
    elif "tech" in event_type:
        risks["high_risk"].append("Technical demo failures")
        risks["medium_risk"].append("Internet connectivity issues")
    
    return risks


def _parse_numeric(value: str) -> int:
    """Extract an integer from user-friendly strings like '500', '500+', '$150,000' or '150000'."""
    if not value:
        return 0
    s = str(value)
    digits = re.findall(r"\d+", s.replace(',', ''))
    if not digits:
        return 0
    # take the first large number
    num = int(digits[0])
    # if the string included a trailing + it probably meant "at least"
    return num


def produce_actionable_plan(event_details: Dict[str, Any], required_agents: List[str]) -> Dict[str, Any]:
    """Produce a compact, actionable event plan WITHOUT a timeline.

    Deliverables (concise):
        - venue: primary + 2 backups (name, city, est. cost, why, next steps + email template)
        - catering: primary + backup (menu highlights, $/person, next steps + email template)
        - speakers: suggested lineup with fees and outreach template
        - budget_summary: category allocations and estimated amounts
        - communications: invitation / reminder / thank-you templates (MCP_PAYLOAD)
        - registration_form: minimal Tally-like schema (fields + validation)
        - vendor_checklist: short checklist items and deadlines
        - risk_assessment

    This is deterministic and uses reasonable assumptions when external agent tools are not available.
    """

    # Assumptions and parsing
    guest_count = _parse_numeric(event_details.get('guest_count', '0'))
    estimated_budget = _parse_numeric(event_details.get('budget_range', '0'))
    if estimated_budget == 0:
        # fallback default
        estimated_budget = 50000

    # Budget allocations (use existing helper)
    allocations = create_budget_breakdown(event_details, required_agents)
    budget_summary = {}
    for cat, pct in allocations.items():
        budget_summary[cat] = {
            'percentage': round(pct * 100, 1),
            'amount': int(round(pct * estimated_budget))
        }

    # Simple venue recommendations (placeholder actionable items)
    location = event_details.get('location_preference', 'Major metro area')
    # generate plausible venue names (these are placeholders - replace with real venues if available)
    def _venue(name_suffix, cost_factor):
        cost = int(budget_summary.get('venue', {}).get('amount', estimated_budget * 0.3) * cost_factor)
        return {
            'name': f"{name_suffix} Venue",
            'city': location,
            'estimated_cost': cost,
            'capacity': guest_count or 100,
            'why': f"Good fit for {event_details.get('event_type')} with capacity for ~{guest_count} attendees.",
            'next_steps': [
                'Confirm availability for the event date',
                'Request venue contract and insurance requirements',
                'Schedule site visit or virtual walkthrough'
            ],
            'booking_email_template': {
                'subject': f"Venue availability and quote request for {event_details.get('event_name')}",
                'body': (
                    f"Hello,\n\nWe're planning '{event_details.get('event_name')}' on {event_details.get('event_date')} "
                    f"and are interested in booking {name_suffix} Venue. Could you confirm availability for that date, "
                    f"capacity details, a sample contract, and an estimated cost?\n\nThank you.\nEvent Organizer"
                )
            }
        }

    venues = [
        _venue('Premier', 1.0),
        _venue('Excellent', 0.75),
        _venue('Budget', 0.5)
    ]

    # Catering recommendations
    per_person_default = int(budget_summary.get('catering', {}).get('amount', int(estimated_budget * 0.25)) / max(guest_count, 1))
    caterers = [
        {
            'name': 'Local Full-Service Caterer',
            'specialty': 'Buffet and plated options with vegetarian/vegan/gluten-free accommodations',
            'menu_highlights': ['Seasonal salad', 'Protein options (meat/vegan)', 'Dessert selection', 'Coffee/tea station'],
            'cost_per_person': per_person_default,
            'next_steps': ['Request sample menus for 3 menu tiers', 'Ask for references from similar-size events'],
            'inquiry_email_template': {
                'subject': f"Catering quote request for {event_details.get('event_name')}",
                'body': (
                    f"Hello,\n\nWe're planning an event for approximately {guest_count} people on {event_details.get('event_date')} in {location}. "
                    f"Please provide sample menus that accommodate vegetarian, vegan, and gluten-free diets and an estimated \${per_person_default}/person cost.\n\nThanks,\nEvent Organizer"
                )
            }
        },
        {
            'name': 'Hotel or Venue In-house Catering',
            'specialty': 'Turnkey options tied to venue booking',
            'menu_highlights': ['Boxed lunches or plated buffets', 'Coffee breaks', 'Beverage packages'],
            'cost_per_person': int(per_person_default * 1.1),
            'next_steps': ['Request bundled venue + catering pricing', 'Confirm service style and staffing plan'],
            'inquiry_email_template': {
                'subject': f"Catering bundle inquiry for {event_details.get('event_name')}",
                'body': (
                    f"Hello,\n\nCan you provide catering options for an event of {guest_count} attendees on {event_details.get('event_date')}? "
                    f"We need vegetarian, vegan, and gluten-free options. Please include staffing and service fees.\n\nThanks,\nEvent Organizer"
                )
            }
        }
    ]

    # Speakers: suggest slots and sample speaker names (placeholders)
    sample_speakers = []
    # create 3 suggested speakers with rough fees depending on 'speakers' budget
    speakers_budget = budget_summary.get('speakers', {}).get('amount', int(estimated_budget * 0.15))
    for i in range(3):
        fee = int(max(500, speakers_budget * (0.35 / (i+1))))
        sample_speakers.append({
            'name': f"Suggested Speaker {i+1}",
            'topic': f"Key insights on {event_details.get('event_type', 'the topic')} - part {i+1}",
            'suggested_fee': fee,
            'outreach_email_template': {
                'subject': f"Speaking invitation: {event_details.get('event_name')}",
                'body': (
                    f"Hello [Name],\n\nWe'd like to invite you to speak at '{event_details.get('event_name')}' on {event_details.get('event_date')}. "
                    f"We expect about {guest_count} attendees and have a speaking honorarium of ${fee}. Please let us know your availability and requirements.\n\nBest,\nEvent Team"
                )
            }
        })

    # Communications templates
    invitation = {
        'subject': f"Invitation: {event_details.get('event_name')} - {event_details.get('event_date')}",
        'plain_text': (
            f"You're invited to {event_details.get('event_name')} on {event_details.get('event_date')} in {location}. "
            f"Join industry leaders to explore {event_details.get('event_type')}. RSVP to reserve your spot."
        ),
        'html': (
            f"<p>You're invited to <strong>{event_details.get('event_name')}</strong> on {event_details.get('event_date')} in {location}.</p>"
            f"<p>Join industry leaders to explore {event_details.get('event_type')}.</p>"
            f"<p><a href='#'>RSVP now</a></p>"
        ),
        'MCP_PAYLOAD': {
            'to': ['attendees@example.com'],
            'subject': f"Invitation: {event_details.get('event_name')}",
            'body_plain': None,
            'body_html': None
        }
    }

    reminder = {
        'subject': f"Reminder: {event_details.get('event_name')} on {event_details.get('event_date')}",
        'body': f"Quick reminder that {event_details.get('event_name')} is coming up on {event_details.get('event_date')}. See you there!"
    }

    thank_you = {
        'subject': f"Thanks for attending {event_details.get('event_name')}",
        'body': f"Thank you for joining us at {event_details.get('event_name')}. We appreciate your participation and feedback."
    }

    # Minimal Tally-like registration form schema
    registration_form = {
        'title': f"{event_details.get('event_name')} Registration",
        'fields': [
            {'id': 'full_name', 'label': 'Full name', 'type': 'text', 'required': True},
            {'id': 'email', 'label': 'Email address', 'type': 'email', 'required': True},
            {'id': 'company', 'label': 'Company / Affiliation', 'type': 'text', 'required': False},
            {'id': 'dietary', 'label': 'Dietary restrictions', 'type': 'multi_select', 'options': ['vegetarian', 'vegan', 'gluten-free', 'none'], 'required': False},
            {'id': 'accessibility', 'label': 'Accessibility needs', 'type': 'text', 'required': False}
        ],
        'privacy': {'collect_emails': True, 'share_with_sponsors': False}
    }

    # Vendor checklist (short)
    vendor_checklist = [
        {'item': 'Sign venue contract', 'due': 'ASAP', 'owner': 'venue'},
        {'item': 'Confirm catering menu and headcount', 'due': '4 weeks before', 'owner': 'catering'},
        {'item': 'Confirm speaker contracts and AV needs', 'due': '8 weeks before', 'owner': 'speakers'},
        {'item': 'Publish registration form and open RSVPs', 'due': '12 weeks before', 'owner': 'registration'},
        {'item': 'Finalize communications and invitations', 'due': '8 weeks before', 'owner': 'communication'}
    ]

    plan = {
        'event_name': event_details.get('event_name'),
        'event_date': event_details.get('event_date'),
        'location': location,
        'guest_count': guest_count,
        'estimated_budget': estimated_budget,
        'venues': venues,
        'caterers': caterers,
        'speakers': sample_speakers,
        'budget_summary': budget_summary,
        'communications': {'invitation': invitation, 'reminder': reminder, 'thank_you': thank_you},
        'registration_form': registration_form,
        'vendor_checklist': vendor_checklist,
        'risk_assessment': create_risk_assessment(event_details, required_agents)
    }

    return plan
