"""AI Event Planner - Pre-filled example for testing."""
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
    
    # Pre-filled event details for testing
    details = {
        "event_type": "tech conference",
        "event_name": "AI Innovation Summit 2026",
        "event_date": "March 15, 2026",
        "location_preference": "San Francisco",
        "budget_range": "$50,000-$100,000",
        "guest_count": "300-500",
        "special_requirements": "AI/ML focus, keynote speakers, networking sessions, accessibility needs"
    }
    
    print("🎉 AI Event Planner - Running with Pre-filled Data")
    print("="*60)
    print("Event Details:")
    for key, value in details.items():
        print(f"  {key}: {value}")
    print("="*60)
    print("\n🚀 Starting event planning workflow...\n")
    
    result = run_event_planning(details)

    print("\n" + "="*60)
    print(f"📋 EVENT PLANNING RESULTS — {details.get('event_name','(unnamed)')}")
    print("="*60)
    
    if isinstance(result, dict):
        # Print summary of outputs
        print(f"\n✅ Planning completed successfully!")
        print(f"\n📁 Generated Outputs:")
        
        if result.get('pdf_generated') and result.get('pdf_report'):
            print(f"   📄 PDF Report: {result['pdf_report']}")
        
        # Try to parse calendar output for ICS file path
        try:
            calendar_data = json.loads(result.get('calendar_invite', '{}'))
            if 'calendar_file_path' in calendar_data:
                print(f"   📅 Calendar File: {calendar_data['calendar_file_path']}")
        except:
            pass
        
        if result.get('registration_form', {}).get('status') == 'success':
            print(f"   📝 Registration Form: {result['registration_form'].get('form_url', 'N/A')}")
        
        print(f"\n📊 Agents Used: {', '.join(result.get('agents_used', []))}")
        
        # Print full result as JSON (can be saved to file)
        print(f"\n{'='*60}")
        print("FULL RESULTS (JSON):")
        print("="*60)
        print(json.dumps(result, indent=2))
    else:
        try:
            print(result.final_output)
        except Exception:
            print(result)
    
    print("="*60)

if __name__ == "__main__":
    main()
