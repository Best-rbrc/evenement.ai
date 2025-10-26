from typing import Dict, List, Any
from tools.budgeting import create_budget_breakdown
from tools import parsing, risk



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
    guest_count = parsing._parse_numeric(event_details.get('guest_count', '0'))
    estimated_budget = parsing._parse_numeric(event_details.get('budget_range', '0'))
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
        'risk_assessment': risk.create_risk_assessment(event_details, required_agents)
    }

    return plan
