"""Test script for the Scheduling Agent with Google OR-Tools."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import os
from dotenv import load_dotenv
from custom_agents.scheduling_agent import create_scheduling_agent
from agents import Runner

# Load environment variables
load_dotenv()


def test_basic_scheduling():
    """Test basic scheduling optimization."""
    print("="*60)
    print("Testing Scheduling Agent - Basic Scenario")
    print("="*60)
    
    agent = create_scheduling_agent()
    
    # Simple test case: 3 sessions, 2 rooms, 2 speakers
    sessions = [
        {"id": 1, "name": "Opening Keynote", "duration": 60, "speaker": "Dr. Weber", "expected_attendees": 150},
        {"id": 2, "name": "Workshop A", "duration": 90, "speaker": "Prof. Schmidt", "expected_attendees": 50},
        {"id": 3, "name": "Panel Discussion", "duration": 60, "speaker": "Dr. Weber", "expected_attendees": 100}
    ]
    
    rooms = [
        {"id": 1, "name": "Main Hall", "capacity": 200, "equipment": ["projector", "mic"]},
        {"id": 2, "name": "Workshop Room", "capacity": 60, "equipment": ["whiteboard", "projector"]}
    ]
    
    speakers = [
        {"id": "Dr. Weber", "name": "Dr. Anna Weber", "travel_time_minutes": 0},
        {"id": "Prof. Schmidt", "name": "Prof. Michael Schmidt", "travel_time_minutes": 0}
    ]
    
    constraints = {
        "event_start": "09:00",
        "event_end": "17:00",
        "lunch_break": "12:00-13:00"
    }
    
    prompt = f"""Please optimize the following event schedule:

Sessions:
{json.dumps(sessions, indent=2)}

Rooms:
{json.dumps(rooms, indent=2)}

Speakers:
{json.dumps(speakers, indent=2)}

Constraints:
{json.dumps(constraints, indent=2)}

Use the optimize_schedule tool to create an optimal schedule."""
    
    print("\nRunning optimization...\n")
    result = Runner.run_sync(agent, prompt)
    
    print("\nResult:")
    print("-"*60)
    print(result.final_output)
    print("="*60)


def test_infeasible_scheduling():
    """Test scheduling with impossible constraints."""
    print("\n\n")
    print("="*60)
    print("Testing Scheduling Agent - Infeasible Scenario")
    print("="*60)
    
    agent = create_scheduling_agent()
    
    # Impossible case: Too many long sessions, not enough time
    sessions = [
        {"id": 1, "name": "Session 1", "duration": 120, "speaker": "Speaker A", "expected_attendees": 100},
        {"id": 2, "name": "Session 2", "duration": 120, "speaker": "Speaker B", "expected_attendees": 100},
        {"id": 3, "name": "Session 3", "duration": 120, "speaker": "Speaker C", "expected_attendees": 100},
        {"id": 4, "name": "Session 4", "duration": 120, "speaker": "Speaker D", "expected_attendees": 100}
    ]
    
    rooms = [
        {"id": 1, "name": "Only Room", "capacity": 150}
    ]
    
    speakers = [
        {"id": "Speaker A", "travel_time_minutes": 0},
        {"id": "Speaker B", "travel_time_minutes": 0},
        {"id": "Speaker C", "travel_time_minutes": 0},
        {"id": "Speaker D", "travel_time_minutes": 0}
    ]
    
    constraints = {
        "event_start": "09:00",
        "event_end": "12:00",  # Only 3 hours but need 8 hours of sessions
        "lunch_break": ""
    }
    
    prompt = f"""Please try to optimize this schedule (which should be impossible):

Sessions:
{json.dumps(sessions, indent=2)}

Rooms:
{json.dumps(rooms, indent=2)}

Speakers:
{json.dumps(speakers, indent=2)}

Constraints:
{json.dumps(constraints, indent=2)}

Use the optimize_schedule tool and explain why it fails if it does."""
    
    print("\nRunning optimization (expecting failure)...\n")
    result = Runner.run_sync(agent, prompt)
    
    print("\nResult:")
    print("-"*60)
    print(result.final_output)
    print("="*60)


if __name__ == "__main__":
    print("🧪 Scheduling Agent Test Suite\n")
    
    try:
        test_basic_scheduling()
        test_infeasible_scheduling()
        
        print("\n\n✅ All tests completed!")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
