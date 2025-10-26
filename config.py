"""Project configuration and small defaults.

This minimal config provides `AGENT_SPECIALIZATIONS` used by the
`custom_agents` factories. The mapping is intentionally simple and can be
extended with richer metadata (prompts, default tools, priority) later.
"""

AGENT_SPECIALIZATIONS = {
    "venue": "Find and evaluate venues suitable for the event.",
    "catering": "Design menus, source caterers, and produce cost estimates.",
    "speakers": "Identify, vet, and schedule speakers or presenters.",
    "programme": "Create the event schedule and session flow.",
    "communication": "Draft invitations, reminders, and post-event messages.",
    "decoration": "Design the event look and feel and vendor requirements.",
    "photography": "Plan photography/videography coverage and deliverables.",
    "music": "Select musical acts, playlists, and AV requirements.",
    "entertainment": "Book entertainers, manage timings and rider needs.",
    "registration": "Create registration forms, ticketing, and check-in flow.",
    "sponsors": "Identify sponsorship opportunities and packages.",
    "seating": "Produce seating plans and accessibility accommodations.",
    "materials": "Manage printed/digital materials, signage and swag.",
    "networking": "Design networking sessions and facilitation aids.",
    "media": "Coordinate press, social media, and live-streaming.",
    "demo": "Organize demos, booths, and technical requirements.",
    "fundraising": "Plan fundraising activities and donor engagement.",
    "activities": "Plan activities, team-building, and side-events.",
    "accommodation": "Source and negotiate room blocks and logistics.",
}
