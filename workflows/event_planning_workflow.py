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
        "communication", "registration", "activities", "entertainment", "budgeting", "scheduling", "calendar", "form"
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
        
        # Special handling for budgeting agent
        if agent_name == "budgeting":
            specialist_prompt = f"""You are the Budgeting specialist for "{event_details['event_name']}", a {event_details['event_type']} event.

{get_current_date_context()}

Event Details:
{json.dumps(event_details, indent=2)}{context}

Your task:
{"INITIAL BUDGET ALLOCATION:" if not specialist_outputs else "BUDGET VALIDATION AND WHAT-IF SCENARIOS:"}

{"1. Create baseline budget allocation across all required categories using calculate_budget_allocation()" if not specialist_outputs else "1. Review all specialist cost estimates"}
{"2. Set priorities based on event type (e.g., venue and catering typically high priority)" if not specialist_outputs else "2. Validate each category cost using validate_category_costs()"}
{"3. Ensure 10-15% contingency fund" if not specialist_outputs else "3. Check if total costs fit within available budget"}
{"4. Provide per-category allocations with rationale" if not specialist_outputs else "4. If over budget, run 2-3 what-if scenarios using run_budget_scenario() to find solutions"}
{"" if not specialist_outputs else "5. Use compare_budget_scenarios() to recommend best approach"}
{"" if not specialist_outputs else "6. Provide itemized breakdown using generate_cost_breakdown() for major categories"}

Required categories for this event: {', '.join([a for a in required_agents if a != 'budgeting' and a not in ['calendar', 'form', 'scheduling']])}

Output comprehensive JSON with budget allocation, scenarios (if applicable), and recommendations."""
        elif agent_name == "scheduling":
            # Special handling for scheduling agent
            specialist_prompt = f"""You are the Advanced Scheduling specialist for "{event_details['event_name']}", a {event_details['event_type']} event.

{get_current_date_context()}

Event Details:
{json.dumps(event_details, indent=2)}{context}

Your task:
1. Extract all sessions/activities from programme and speakers outputs
2. Identify available rooms from venue output
3. Determine speaker availability and travel time requirements
4. Define constraints (event hours, lunch breaks, capacity requirements)
5. Use optimize_schedule() to create optimal schedule that:
   - Avoids all conflicts (rooms, speakers, capacity)
   - Respects break times
   - Minimizes total duration
   - Maximizes room utilization

Input format for optimize_schedule:
- sessions: [{{"id": 1, "name": "Session Name", "duration": 60, "speaker": "Speaker Name", "expected_attendees": 100}}]
- rooms: [{{"id": 1, "name": "Room Name", "capacity": 150, "equipment": ["projector"]}}]
- speakers: [{{"id": "Speaker Name", "travel_time_minutes": 30}}]
- constraints: {{"event_start": "09:00", "event_end": "18:00", "lunch_break": "12:00-13:00"}}

If scheduling is infeasible, explain conflicts and provide actionable suggestions.

Output comprehensive JSON with optimized schedule, metrics, and any conflict resolutions."""
        else:
            # Add budget context if budgeting agent has run
            budget_context = ""
            if "budgeting" in specialist_outputs:
                budget_context = f"\n\nBUDGET CONSTRAINTS from Budgeting Specialist:\n{specialist_outputs['budgeting']}\n\nPlease ensure your recommendations fit within your allocated budget."
            
            specialist_prompt = f"""You are the {agent_name} specialist for "{event_details['event_name']}", a {event_details['event_type']} event.

{get_current_date_context()}

Event Details:
{json.dumps(event_details, indent=2)}{context}{budget_context}

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
   - Budget conflicts (total cost vs available budget) - IF BUDGETING AGENT RAN: Check their scenario analysis
   - Logical inconsistencies (e.g., venue capacity vs guest count)
   - Missing critical information
   - Interdependencies and conflicts

2. BUDGET VALIDATION (CRITICAL):
   - IF budgeting agent was NOT used yet: Handoff to budgeting agent NOW to validate all costs
   - IF budgeting agent shows over_budget scenarios: Consider their recommended scenario
   - Ensure final plan reflects budgeting agent's approved allocation

2.5. SCHEDULING OPTIMIZATION REVIEW (IF SCHEDULING AGENT WAS USED):
   - Extract and preserve scheduling metrics (total_duration, room_utilization, conflicts_resolved)
   - Include optimized schedule in final plan under "schedule" section
   - Highlight any scheduling conflicts that were resolved
   - If scheduling was infeasible, document the conflicts and suggestions

3. IF YOU IDENTIFY OTHER ISSUES OR GAPS:
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
  "schedule": {{
    "optimized": true/false,
    "sessions": [...],  // REQUIRED if scheduling agent was used
    "metrics": {{
      "total_duration": "...",
      "event_ends_at": "...",
      "room_utilization": {{}},
      "conflicts_resolved": "..."
    }},
    "status": "optimal | feasible | infeasible"  // from scheduling agent output
  }},
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
    # PHASE 4: Event Outputs (CALENDAR & REGISTRATION FORM)
    # ============================================================
    print(f"\n{'='*60}")
    print("📅 PHASE 4: Event Outputs (Calendar & Registration Form)")
    print(f"{'='*60}\n")
    
    # Create calendar invite
    print("Creating calendar invite file...\n")
    
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
    
    # Create registration form
    print("Creating event registration form...\n")
    
    form_agent = all_specialists["form"]
    
    form_prompt = f"""Create a registration form for "{event_details['event_name']}".

Event Details:
{json.dumps(event_details, indent=2)}

Specialist Planning Context:
{json.dumps(specialist_outputs, indent=2)}

Final Plan Summary:
{final_result.final_output[:1500]}...

Use the complete event context above to design an appropriate registration form with relevant fields for this {event_details.get('event_type')} event."""

    # Retry logic for rate limiting
    import asyncio
    max_retries = 3
    form_result = None
    
    for attempt in range(max_retries):
        try:
            form_result = Runner.run_sync(form_agent, form_prompt)
            break
        except Exception as e:
            if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"⏳ Rate limit hit. Waiting {wait_time}s before retry...\n")
                import time
                time.sleep(wait_time)
            else:
                print(f"⚠️  Form creation error: {e}\n")
                form_result = type('obj', (object,), {'final_output': '{"status": "error", "message": "Form creation failed"}'})()
                break
    
    # Extract form URL from output
    from custom_agents.form_agent import extract_form_url_from_output
    form_data = extract_form_url_from_output(form_result.final_output if form_result else "")
    
    if form_data.get("status") == "success":
        print(f"✅ Registration form created: {form_data.get('form_url')}\n")
    else:
        print(f"⚠️  Form creation had issues. Check output for details.\n")
    
    # Return comprehensive results
    return {
        "event_details": event_details,
        "planning_phase": planning_result.final_output,
        "specialist_outputs": specialist_outputs,
        "final_plan": final_result.final_output,
        "calendar_invite": calendar_result.final_output,
        "registration_form": form_data,
        "agents_used": required_agents + ["calendar", "form"],
        "success": True
    }


