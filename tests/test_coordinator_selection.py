"""Quick test to verify coordinator selects scheduling agent for conferences."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from agents import Runner
from custom_agents.base import create_specialized_agents
from custom_agents.coordinator_agent import create_coordinator_agent
import datetime
from dotenv import load_dotenv

load_dotenv()


def get_current_date_context() -> str:
    current_date = datetime.datetime.now()
    return f"Today's date: {current_date.strftime('%B %d, %Y')} ({current_date.strftime('%Y-%m-%d')})"


def test_conference_selection():
    """Test that coordinator selects scheduling for a conference."""
    print("="*60)
    print("Test: Coordinator Agent Selection for Conference")
    print("="*60)
    
    event_details = {
        "event_name": "AI & ML Summit 2025",
        "event_type": "tech conference",
        "event_date": "March 15-16, 2025",
        "location_preference": "San Francisco",
        "budget_range": "$50,000-$75,000",
        "guest_count": "200-250",
        "special_requirements": "Need 3 parallel tracks, 10 speakers, multiple sessions, workshop spaces"
    }
    
    all_agent_types = [
        "venue", "catering", "programme", "speakers", 
        "communication", "registration", "activities", "entertainment", 
        "budgeting", "scheduling", "calendar", "form"
    ]
    
    all_specialists = create_specialized_agents(all_agent_types)
    coordinator = create_coordinator_agent(event_details, all_agent_types, all_specialists)
    
    planning_prompt = f"""You are the Event Planning Coordinator analyzing requirements for "{event_details['event_name']}".

{get_current_date_context()}

Event Details:
{json.dumps(event_details, indent=2)}

Your task for PHASE 1 - STRATEGIC PLANNING:

1. Analyze the event type, budget, guest count, and special requirements
2. Decide which specialist agents are needed for this event
3. Determine the optimal ORDER to call them (e.g., venue first, then catering based on venue kitchen)
4. Identify any special considerations or constraints

Available specialists:
- venue: Physical location selection and logistics
- catering: Food, beverages, and dining service
- programme: Event schedule and session planning
- speakers: Speaker/presenter coordination
- communication: Marketing, invitations, attendee communications
- registration: Registration systems and check-in
- activities: Team-building and recreational activities
- entertainment: Entertainment and performance coordination
- budgeting: Budget allocation, what-if scenarios, cost validation
- scheduling: Advanced constraint-based schedule optimization (resolves conflicts, optimizes room/speaker assignments)
- calendar: Calendar invites and ICS file generation
- form: Online registration/RSVP form creation (auto-generated in Phase 4)

Output your plan as JSON:
{{
  "analysis": "Brief analysis of event needs",
  "required_agents": ["agent1", "agent2", ...],  // In optimal execution order
  "execution_order_rationale": "Why this order makes sense",
  "special_considerations": ["consideration1", "consideration2", ...]
}}

IMPORTANT GUIDELINES:
- ALWAYS include "budgeting" agent early in the sequence (typically after venue/catering needs are identified)
- Budgeting should run BEFORE cost-heavy agents provide estimates (so they have allocation targets)
- OR budgeting can run AFTER specialists to validate and create what-if scenarios

- WHEN TO USE "scheduling" agent (CRITICAL):
  * USE for: conferences, workshops, summits, multi-day events, academic events
  * USE when: Multiple sessions, speakers, or parallel tracks need coordination
  * USE when: Multiple rooms/venues need to be scheduled without conflicts
  * SKIP for: Simple single-session events (weddings, birthday parties, single galas)
  * SKIP for: Events with one linear timeline (no room/speaker conflicts possible)
  * PLACEMENT: AFTER programme, speakers, and venue agents (needs their output as input)
  * BEFORE calendar agent (provides optimized times for calendar generation)

- Be strategic and selective - don't include agents that aren't truly needed for this event type."""

    print("\nRunning coordinator planning...\n")
    result = Runner.run_sync(coordinator, planning_prompt)
    
    try:
        planning_data = json.loads(result.final_output)
        required_agents = planning_data.get("required_agents", [])
        
        print("="*60)
        print("RESULTS")
        print("="*60)
        print(f"\n✓ Selected agents: {', '.join(required_agents)}")
        print(f"\n💡 Rationale: {planning_data.get('execution_order_rationale', 'N/A')}")
        
        # Check if scheduling was selected
        has_scheduling = 'scheduling' in required_agents
        print(f"\n{'✅' if has_scheduling else '❌'} Scheduling agent selected: {has_scheduling}")
        
        if has_scheduling:
            # Check placement
            scheduling_idx = required_agents.index('scheduling')
            programme_idx = required_agents.index('programme') if 'programme' in required_agents else -1
            speakers_idx = required_agents.index('speakers') if 'speakers' in required_agents else -1
            venue_idx = required_agents.index('venue') if 'venue' in required_agents else -1
            
            print(f"\n📍 Agent order:")
            for i, agent in enumerate(required_agents):
                marker = "👉" if agent == 'scheduling' else "  "
                print(f"   {marker} {i+1}. {agent}")
            
            # Verify placement
            correct_placement = True
            if programme_idx >= 0 and scheduling_idx < programme_idx:
                print(f"\n⚠️  Scheduling ({scheduling_idx}) should come AFTER programme ({programme_idx})")
                correct_placement = False
            if speakers_idx >= 0 and scheduling_idx < speakers_idx:
                print(f"\n⚠️  Scheduling ({scheduling_idx}) should come AFTER speakers ({speakers_idx})")
                correct_placement = False
            if venue_idx >= 0 and scheduling_idx < venue_idx:
                print(f"\n⚠️  Scheduling ({scheduling_idx}) should come AFTER venue ({venue_idx})")
                correct_placement = False
            
            if correct_placement:
                print(f"\n✅ Scheduling agent correctly placed after dependencies!")
        else:
            print(f"\n❌ PROBLEM: Scheduling agent NOT selected for multi-session conference!")
            print(f"   Event has: 3 parallel tracks, 10 speakers, multiple sessions")
            print(f"   This SHOULD trigger scheduling agent usage!")
        
        return has_scheduling
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Failed to parse planning output: {e}")
        print(f"\nRaw output:\n{result.final_output}")
        return False


def test_wedding_selection():
    """Test that coordinator does NOT select scheduling for a simple wedding."""
    print("\n\n" + "="*60)
    print("Test: Coordinator Agent Selection for Wedding")
    print("="*60)
    
    event_details = {
        "event_name": "Sarah & John's Wedding",
        "event_type": "wedding",
        "event_date": "June 20, 2025",
        "location_preference": "Outdoor venue",
        "budget_range": "$20,000-$30,000",
        "guest_count": "100-120",
        "special_requirements": "Outdoor ceremony, vegetarian options, photographer needed"
    }
    
    all_agent_types = [
        "venue", "catering", "programme", "speakers", 
        "communication", "registration", "activities", "entertainment", 
        "budgeting", "scheduling", "calendar", "form"
    ]
    
    all_specialists = create_specialized_agents(all_agent_types)
    coordinator = create_coordinator_agent(event_details, all_agent_types, all_specialists)
    
    planning_prompt = f"""You are the Event Planning Coordinator analyzing requirements for "{event_details['event_name']}".

{get_current_date_context()}

Event Details:
{json.dumps(event_details, indent=2)}

[Same prompt as above with scheduling guidelines...]

WHEN TO USE "scheduling" agent (CRITICAL):
  * USE for: conferences, workshops, summits, multi-day events, academic events
  * USE when: Multiple sessions, speakers, or parallel tracks need coordination
  * SKIP for: Simple single-session events (weddings, birthday parties, single galas)
  * SKIP for: Events with one linear timeline (no room/speaker conflicts possible)

Your task: Decide which agents are needed and output as JSON."""

    print("\nRunning coordinator planning...\n")
    result = Runner.run_sync(coordinator, planning_prompt)
    
    try:
        planning_data = json.loads(result.final_output)
        required_agents = planning_data.get("required_agents", [])
        
        print("="*60)
        print("RESULTS")
        print("="*60)
        print(f"\n✓ Selected agents: {', '.join(required_agents)}")
        
        has_scheduling = 'scheduling' in required_agents
        print(f"\n{'⚠️' if has_scheduling else '✅'} Scheduling agent selected: {has_scheduling}")
        
        if not has_scheduling:
            print(f"✅ CORRECT: Scheduling NOT needed for simple linear wedding event")
        else:
            print(f"❌ PROBLEM: Scheduling selected but not needed for simple wedding")
        
        return not has_scheduling
        
    except:
        return False


if __name__ == "__main__":
    print("🧪 Coordinator Agent Selection Test\n")
    
    test1 = test_conference_selection()
    test2 = test_wedding_selection()
    
    print("\n\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Conference test (should select scheduling): {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Wedding test (should NOT select scheduling): {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎉 All tests passed! Coordinator correctly identifies when to use scheduling.")
    else:
        print("\n⚠️  Some tests failed - coordinator may need prompt refinement.")
