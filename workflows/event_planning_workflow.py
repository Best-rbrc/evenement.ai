"""High level workflow entrypoint for event planning.

Intelligent 3-phase workflow:
1. Coordinator analyzes event and decides which agents to use + order
2. Run those agents and collect outputs
3. Coordinator reviews, refines, and finalizes (can call new agents if needed)

Design:
- Coordinator makes strategic decisions (which agents, what order, what refinements)
- Specialists do domain-specific work
- Coordinator can iterate and call additional agents as needed
"""
from typing import Dict, Any, List
import json
import datetime


def get_current_date_context() -> str:
    """Get current date context for agents."""
    current_date = datetime.datetime.now()
    return f"Today's date: {current_date.strftime('%B %d, %Y')} ({current_date.strftime('%Y-%m-%d')})"


def run_event_planning(event_details: Dict[str, Any]) -> Dict[str, Any]:
    """Intelligent multi-phase workflow with coordinator orchestration.

    Phase 1: Coordinator Planning
    - Analyzes event requirements
    - Decides which specialists are needed
    - Determines optimal order of execution

    Phase 2: Specialist Execution
    - Calls each specialist in the determined order
    - Collects all outputs

    Phase 3: Coordinator Finalization
    - Reviews all specialist outputs
    - Identifies gaps, conflicts, or issues
    - Calls additional agents if needed
    - Produces final unified plan
    """
    # Import SDK components
    try:
        from agents import Runner
        from custom_agents.base import create_specialized_agents
        from custom_agents.coordinator_agent import create_coordinator_agent
    except Exception as exc:
        raise RuntimeError(f"Required imports failed: {exc}")

    print(f"\n{'='*60}")
    print(f"🎉 AI EVENT PLANNER")
    print(f"{'='*60}")
    print(f"Event: {event_details['event_name']}")
    print(f"Type: {event_details['event_type']}")
    print(f"Date Context: {get_current_date_context()}")
    print(f"{'='*60}\n")

    # ============================================================
    # PHASE 1: COORDINATOR PLANNING
    # ============================================================
    print("📋 PHASE 1: Strategic Planning\n")
    print("Coordinator analyzing event requirements...\n")

    # Create all available specialists (coordinator will decide which to use)
    all_agent_types = [
        "venue", "catering", "programme", "speakers", 
        "communication", "registration", "activities", "entertainment", "calendar"
    ]
    all_specialists = create_specialized_agents(all_agent_types)
    
    # Create coordinator with handoffs to all specialists
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
- calendar: Calendar invites and ICS file generation

Output your plan as JSON:
{{
  "analysis": "Brief analysis of event needs",
  "required_agents": ["agent1", "agent2", ...],  // In optimal execution order
  "execution_order_rationale": "Why this order makes sense",
  "special_considerations": ["consideration1", "consideration2", ...]
}}

Be strategic and selective - don't include agents that aren't truly needed for this event type."""

    planning_result = Runner.run_sync(coordinator, planning_prompt)
    
    # Parse the planning decision
    try:
        planning_data = json.loads(planning_result.final_output)
        required_agents = planning_data.get("required_agents", all_agent_types[:6])
        print(f"✅ Planning complete!")
        print(f"\n� Selected agents (in order): {', '.join(required_agents)}")
        print(f"💡 Rationale: {planning_data.get('execution_order_rationale', 'N/A')}\n")
    except:
        # Fallback if parsing fails
        required_agents = all_agent_types[:6]
        print(f"⚠️  Using default agent selection\n")

    # ============================================================
    # PHASE 2: SPECIALIST EXECUTION
    # ============================================================
    print(f"\n{'='*60}")
    print("🔧 PHASE 2: Specialist Execution")
    print(f"{'='*60}\n")
    
    specialist_outputs = {}
    
    for idx, agent_name in enumerate(required_agents, 1):
        if agent_name not in all_specialists:
            print(f"⚠️  Skipping unknown agent: {agent_name}")
            continue
            
        agent = all_specialists[agent_name]
        
        print(f"[{idx}/{len(required_agents)}] 🎯 {agent_name.title()} Specialist")
        print(f"{'─'*40}")
        
        # Build context-aware prompt with prior outputs
        context = ""
        if specialist_outputs:
            context = f"\n\nPrevious specialist outputs for context:\n{json.dumps(specialist_outputs, indent=2)}"
        
        specialist_prompt = f"""You are the {agent_name} specialist for "{event_details['event_name']}", a {event_details['event_type']} event.

{get_current_date_context()}

Event Details:
{json.dumps(event_details, indent=2)}{context}

Your task:
Provide detailed, actionable recommendations for {agent_name}, including:
- Specific options with names and costs where applicable
- Timeline and logistics considerations
- Budget estimates (itemized)
- Top recommendations with rationale
- Any dependencies on other areas

Output structured JSON with your recommendations."""

        result = Runner.run_sync(agent, specialist_prompt)
        specialist_outputs[agent_name] = result.final_output
        
        print(f"✓ Complete\n")

    # ============================================================
    # PHASE 3: COORDINATOR FINALIZATION
    # ============================================================
    print(f"\n{'='*60}")
    print("🎯 PHASE 3: Review, Refinement & Finalization")
    print(f"{'='*60}\n")
    
    print("Coordinator reviewing all outputs...\n")

    finalization_prompt = f"""You are the Event Planning Coordinator finalizing the plan for "{event_details['event_name']}".

{get_current_date_context()}

You have received outputs from these specialists: {', '.join(required_agents)}

Event Details:
{json.dumps(event_details, indent=2)}

All Specialist Outputs:
{json.dumps(specialist_outputs, indent=2)}

Your task for PHASE 3 - FINALIZATION:

1. REVIEW all specialist outputs for:
   - Budget conflicts (total cost vs available budget)
   - Logical inconsistencies (e.g., venue capacity vs guest count)
   - Missing critical information
   - Interdependencies and conflicts

2. IF YOU IDENTIFY ISSUES OR GAPS:
   - You can handoff to ANY specialist agent (even ones not called yet) to:
     * Refine their recommendations with adjusted constraints
     * Fill in missing information
     * Resolve conflicts with other areas
   - Example: "Venue costs exceed budget - handoff to venue agent with reduced budget"
   - Example: "We need decoration planning - handoff to decoration agent"

3. SYNTHESIZE the final comprehensive event plan including:
   - Executive summary (2-3 paragraphs)
   - Complete event timeline (with all areas integrated)
   - Detailed budget breakdown by category with totals
   - All specialist recommendations (organized and refined)
   - Risk assessment with mitigation strategies
   - Prioritized action items with deadlines
   - Assumptions made

4. OUTPUT as valid JSON:
{{
  "executive_summary": "...",
  "timeline": [
    {{"phase": "...", "tasks": [...], "deadline": "..."}}
  ],
  "budget": {{
    "total_available": "...",
    "total_allocated": "...",
    "by_category": {{}},
    "status": "within_budget | over_budget | at_limit"
  }},
  "recommendations": {{
    "venue": {{}},
    "catering": {{}},
    ...
  }},
  "risks": [
    {{"risk": "...", "severity": "high|medium|low", "mitigation": "..."}}
  ],
  "action_items": [
    {{"action": "...", "owner": "...", "deadline": "...", "priority": "high|medium|low"}}
  ],
  "assumptions": [...]
}}

Use handoffs if needed to refine or add information. Then provide your final synthesized plan."""

    final_result = Runner.run_sync(coordinator, finalization_prompt)
    
    print("✅ Finalization complete!\n")
    
    # ============================================================
    # PHASE 4: Event Outputs e.g. CALENDAR GENERATION 
    # ============================================================
    print(f"\n{'='*60}")
    print("📅 PHASE 4: Event Outputs e.g. CALENDAR GENERATION")
    print(f"{'='*60}\n")
    
    print("Creating calendar invite file...\n")
    
    # Always create calendar invite as final step
    calendar_agent = all_specialists["calendar"]
    
    calendar_prompt = f"""You are the Calendar Specialist for "{event_details['event_name']}".

{get_current_date_context()}

Event Details:
{json.dumps(event_details, indent=2)}

All Planning Outputs:
{json.dumps(specialist_outputs, indent=2)}

Final Plan:
{final_result.final_output}

Your task:
Create a comprehensive calendar invite (.ics file) for this event including:

1. **Extract Key Information:**
   - Event name, date, and location
   - Determine appropriate start and end times based on event type and outputs
   - Create rich description from planning details

2. **Generate Calendar File:**
   - Use the generate_ics_file tool to create the .ics file
   - Include venue information from venue specialist
   - Add timing from programme specialist if available
   - Set appropriate reminders and notifications

3. **Provide File Details:**
   - Confirm successful file creation
   - Provide file path for user access
   - Include instructions for importing to calendar apps

Output JSON with:
- calendar_file_path
- event_summary
- timing_details
- import_instructions"""

    calendar_result = Runner.run_sync(calendar_agent, calendar_prompt)
    
    print("✅ Calendar invite generated!\n")
    
    # Return comprehensive results
    return {
        "event_details": event_details,
        "planning_phase": planning_result.final_output,
        "specialist_outputs": specialist_outputs,
        "final_plan": final_result.final_output,
        "calendar_invite": calendar_result.final_output,
        "agents_used": required_agents + ["calendar"],
        "success": True
    }


