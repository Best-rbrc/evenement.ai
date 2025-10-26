"""Configuration settings for the AI Event Planner."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Event types and their required agents
EVENT_TYPES = {
    "wedding": ["venue", "catering", "decoration", "photography", "music", "communication"],
    "corporate_conference": ["venue", "catering", "speakers", "programme", "communication", "registration"],
    "tech_conference": ["venue", "catering", "speakers", "programme", "communication", "registration", "sponsors"],
    "birthday_party": ["venue", "catering", "decoration", "entertainment", "communication"],
    "gala_dinner": ["venue", "catering", "decoration", "entertainment", "communication", "seating"],
    "workshop": ["venue", "catering", "speakers", "programme", "communication", "materials"],
    "networking_event": ["venue", "catering", "communication", "registration", "networking"],
    "product_launch": ["venue", "catering", "speakers", "programme", "communication", "media", "demo"],
    "charity_fundraiser": ["venue", "catering", "speakers", "programme", "communication", "fundraising"],
    "retreat": ["venue", "catering", "programme", "communication", "activities", "accommodation"]
}

# Agent specializations
AGENT_SPECIALIZATIONS = {
    "venue": "Specializes in venue selection, booking, and logistics",
    "catering": "Handles food and beverage planning, menu selection, and dietary requirements",
    "speakers": "Manages speaker recruitment, contracts, and presentation logistics",
    "programme": "Creates event schedules, timing, and program flow",
    "communication": "Handles invitations, marketing, and attendee communication",
    "decoration": "Manages event decoration, theming, and visual design",
    "photography": "Coordinates photography and videography services",
    "music": "Handles music, entertainment, and audio-visual requirements",
    "entertainment": "Manages entertainment, activities, and guest engagement",
    "registration": "Manages attendee registration and check-in processes",
    "sponsors": "Handles sponsor relationships and benefits",
    "seating": "Manages seating arrangements and table planning",
    "materials": "Coordinates workshop materials and supplies",
    "networking": "Facilitates networking activities and connections",
    "media": "Handles media relations and press coverage",
    "demo": "Coordinates product demonstrations and showcases",
    "fundraising": "Manages fundraising activities and donor relations",
    "activities": "Plans recreational and team-building activities",
    "accommodation": "Handles accommodation booking and logistics"
}
