"""AI Event Planner - CLI input and workflow call."""
import json
import os
import sys
import asyncio
from dotenv import load_dotenv
from workflows.event_planning_workflow import run_event_planning

# Load environment variables from .env file if it exists
load_dotenv()

def check_api_key():
    """Check if OpenAI API key is set and show helpful error if not."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\n" + "="*60)
        print("❌ ERROR: OpenAI API Key Not Found")
        print("="*60)
        print("The OpenAI Agents SDK requires an API key to run.")
        print("\nTo fix this, set your API key:")
        print("  export OPENAI_API_KEY=sk-...your-key-here...")
        print("\nOr create a .env file with:")
        print("  OPENAI_API_KEY=sk-...your-key-here...")
        print("\nGet your API key at: https://platform.openai.com/api-keys")
        print("="*60 + "\n")
        sys.exit(1)
    return api_key

def collect_event_details():
    """Collect basic event information from the user."""
    print("🎉 Welcome to the AI Event Planner!")
    print("I'll help you plan your event by asking a few key questions.\n")

    event_type = input("What type of event are you planning? (e.g., wedding, corporate conference, tech conference, birthday party, gala dinner, workshop, networking event, product launch, charity fundraiser, retreat): ").strip().lower()
    event_name = input("What's the name of your event? ").strip()
    event_date = input("When is your event? (e.g., 'March 15, 2024' or 'Q2 2024'): ").strip()
    location_preference = input("Do you have a preferred location or city? (or 'flexible'): ").strip()
    budget_range = input("What's your approximate budget range? (e.g., '$5,000-$10,000', 'under $2,000', 'flexible'): ").strip()
    guest_count = input("How many guests/attendees are you expecting? (e.g., '50-100', '200+', 'flexible'): ").strip()
    special_requirements = input("Any special requirements or themes? (e.g., 'outdoor venue', 'vegetarian catering', 'accessibility needs', 'corporate theme'): ").strip()

    return {
        "event_type": event_type,
        "event_name": event_name,
        "event_date": event_date,
        "location_preference": location_preference,
        "budget_range": budget_range,
        "guest_count": guest_count,
        "special_requirements": special_requirements
    }

def main():
    check_api_key()
    # Ensure there is an asyncio event loop for libraries that call get_event_loop()
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        try:
            # Set a default policy and loop for Python 3.13+
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
        except Exception:
            pass
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    details = collect_event_details()
    result = run_event_planning(details)

    print("\n" + "="*60)
    print(f"📋 EVENT PLANNING RESULTS — {details.get('event_name','(unnamed)')}")
    print("="*60)
    if isinstance(result, dict):
        print(json.dumps(result, indent=2))
    else:
        try:
            print(result.final_output)
        except Exception:
            print(result)
    print("="*60)

if __name__ == "__main__":
    main()