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
import asyncio


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
    # Ensure an asyncio event loop exists for sync runner on Python 3.13+
    def _ensure_loop():
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            loop_local = asyncio.new_event_loop()
            asyncio.set_event_loop(loop_local)

    _ensure_loop()

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

    # Run coordinator planning with rate-limit aware retries
    _ensure_loop()
    def _run_sync_with_backoff(agent, prompt, max_retries: int = 3):
        import time, re, random
        last_exc = None
        for attempt in range(max_retries):
            try:
                _ensure_loop()
                return Runner.run_sync(agent, prompt)
            except Exception as e:
                last_exc = e
                msg = str(e)
                if "rate_limit_exceeded" in msg or "Please try again in" in msg:
                    # Parse suggested wait, else exponential backoff
                    wait_time = 2 ** attempt
                    m = re.search(r"Please try again in\s+([0-9]+\.?[0-9]*)s", msg)
                    if m:
                        try:
                            wait_time = float(m.group(1))
                        except Exception:
                            pass
                    wait_time += random.uniform(0.3, 0.7)
                    print(f"⏳ Rate limit. Waiting {wait_time:.2f}s before retry...\n")
                    time.sleep(wait_time)
                    continue
                else:
                    break
        raise last_exc

    planning_result = _run_sync_with_backoff(coordinator, planning_prompt)
    
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

        _ensure_loop()
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

    _ensure_loop()
    final_result = _run_sync_with_backoff(coordinator, finalization_prompt)
    
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

    _ensure_loop()
    calendar_result = Runner.run_sync(calendar_agent, calendar_prompt)
    
    print("✅ Calendar invite generated!\n")
    
    # Create registration form
    print("Creating event registration form...\n")
    
    form_agent = all_specialists["form"]  # Kept for consistency, but we'll manage a fresh MCP context per attempt

    # Compact prompt to reduce tokens: only essentials
    concise_event = {
        "event_name": event_details.get("event_name"),
        "event_type": event_details.get("event_type"),
        "event_date": event_details.get("event_date"),
        "location": event_details.get("location_preference"),
        "guest_count": event_details.get("guest_count"),
        "special_requirements": event_details.get("special_requirements"),
    }
    # Derive any minimal context from specialists without full dumps
    minimal_context = {}
    if "venue" in specialist_outputs:
        minimal_context["venue"] = "include venue/address field if available"
    if "catering" in specialist_outputs:
        minimal_context["catering"] = "collect dietary restrictions"
    if "registration" in specialist_outputs:
        minimal_context["registration"] = "ensure attendance and contact fields"
    if "programme" in specialist_outputs:
        minimal_context["programme"] = "optional session preferences"

    form_prompt = (
        f"Create an RSVP/registration form for '{event_details.get('event_name')}'.\n\n"
        f"Essentials: {json.dumps(concise_event, indent=2)}\n\n"
        f"Guidelines: {json.dumps(minimal_context, indent=2)}\n\n"
        "Return ONLY valid JSON with: {\"form_url\": \"https://tally.so/r/xxxxx\", \"status\": \"success\"}."
    )

    # Helper: run the form step with a dedicated MCP stdio context (mirrors your working script)
    async def _run_form_once(prompt: str):
        import os
        import re
        import json as _json
        from agents import Agent as _Agent, Runner as _Runner
        from agents.mcp import MCPServerStdio as _MCPServerStdio
        from agents.model_settings import ModelSettings as _ModelSettings

        tally = _MCPServerStdio({
            "command": "npx",
            "args": [
                "mcp-remote",
                "https://api.tally.so/mcp",
                "--header", f"Authorization: Bearer {os.getenv('TALLY_API_KEY','')}",
            ],
        })

        model_settings = _ModelSettings(max_tokens=4000, temperature=0.7)

        agent = _Agent(
            name="Tally Form Agent",
            instructions=(
                "Use the Tally MCP tools to create an RSVP/registration form. "
                "After successful form creation, return ONLY valid JSON: "
                '{"form_url": "https://tally.so/r/xxxxx", "status": "success"}. '
                "No extra text or markdown."
            ),
            mcp_servers=[tally],
            model_settings=model_settings,
        )

        # Allow overriding the model used for this step via env FORM_MODEL
        # If supported by the SDK, it will read the OPENAI_MODEL env var.
        prev_model = os.environ.get("OPENAI_MODEL")
        form_model = os.environ.get("FORM_MODEL")
        if form_model:
            os.environ["OPENAI_MODEL"] = form_model
        try:
            async with tally:
                result = await _Runner.run(agent, prompt)
        finally:
            # Restore previous model env to avoid side effects on other steps
            if form_model is not None:
                if prev_model is None:
                    os.environ.pop("OPENAI_MODEL", None)
                else:
                    os.environ["OPENAI_MODEL"] = prev_model
            return result

    # Retry logic for transient errors (rate limits, remote SSE timeouts)
    max_retries = 5
    form_result = None
    
    for attempt in range(max_retries):
        try:
            _ensure_loop()
            # Prefer the managed-context path which reliably opens/closes the MCP stdio bridge
            loop = asyncio.get_event_loop()
            form_result = loop.run_until_complete(_run_form_once(form_prompt))
            break
        except Exception as e:
            err_text = str(e)
            is_transient = (
                "rate_limit" in err_text.lower()
                or "StreamableHTTPError" in err_text
                or "SSE" in err_text
                or " 524" in err_text
            )
            if is_transient and attempt < max_retries - 1:
                import time, random, re
                # Start with exponential backoff
                base_wait = 2 ** attempt
                reason = "rate limit" if "rate_limit" in err_text.lower() else "remote connection"
                # Parse server-provided wait hint: "Please try again in Xs"
                match = re.search(r"Please try again in\s+([0-9]+\.?[0-9]*)s", err_text)
                if match:
                    try:
                        base_wait = float(match.group(1))
                    except Exception:
                        pass
                # Apply a multiplier and clamp to a sensible range
                wait_time = max(5.0, min(30.0, base_wait * 1.5))
                # Add jitter to avoid thundering herd
                wait_time += random.uniform(0.5, 1.2)
                print(f"⏳ Transient {reason} issue. Waiting {wait_time:.2f}s before retry...\n")
                time.sleep(wait_time)
                continue
            else:
                print(f"⚠️  Form creation error: {e}\n")
                form_result = type('obj', (object,), {'final_output': '{"status": "error", "message": "Form creation failed"}'})()
                break
    
    # Extract form URL from output; on failure, create a local fallback schema
    from custom_agents.form_agent import extract_form_url_from_output
    form_data = extract_form_url_from_output(form_result.final_output if form_result else "")

    if form_data.get("status") == "success":
        print(f"✅ Registration form created: {form_data.get('form_url')}\n")
    else:
        print(f"⚠️  Remote form creation had issues. Generating local fallback schema...\n")
        try:
            import os, json as _json
            os.makedirs("event_outputs", exist_ok=True)
            # Minimal, useful form schema based on available details
            fallback_schema = {
                "title": f"Registration — {event_details.get('event_name','Event')}",
                "fields": [
                    {"id": "name", "label": "Full Name", "type": "text", "required": True},
                    {"id": "email", "label": "Email", "type": "email", "required": True},
                    {"id": "attendance", "label": "Will you attend?", "type": "select", "options": ["Yes", "No"], "required": True},
                    {"id": "affiliation", "label": "Affiliation / Company", "type": "text", "required": False},
                    {"id": "dietary", "label": "Dietary Restrictions", "type": "text", "required": False},
                    {"id": "accessibility", "label": "Accessibility Needs", "type": "text", "required": False}
                ],
                "event": {
                    "name": event_details.get('event_name'),
                    "type": event_details.get('event_type'),
                    "date": event_details.get('event_date'),
                    "location": event_details.get('location_preference')
                }
            }
            safe_event_name = "".join(c for c in event_details.get('event_name','event') if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
            fallback_path = os.path.join("event_outputs", f"registration_form_{safe_event_name}.json")
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write(_json.dumps(fallback_schema, indent=2))
            form_data = {
                "status": "deferred",
                "message": "Remote form creation failed due to rate limits/connection. Local form schema generated.",
                "local_schema_path": fallback_path
            }
            print(f"✅ Local form schema saved: {fallback_path}\n")
        except Exception as _e:
            print(f"⚠️  Failed to write local form schema: {_e}\n")
    
    # ============================================================
    # PHASE 5: PDF REPORT GENERATION
    # ============================================================
    print(f"\n{'='*60}")
    print("📄 PHASE 5: Generating Professional PDF Report")
    print(f"{'='*60}\n")
    
    print("Creating comprehensive PDF proposal...\n")
    
    try:
        from tools.report_generator import generate_event_proposal_pdf
        
        # Parse final plan if it's a string
        final_plan_dict = final_result.final_output
        if isinstance(final_plan_dict, str):
            try:
                final_plan_dict = json.loads(final_plan_dict)
            except:
                # If parsing fails, create a basic structure
                final_plan_dict = {
                    "executive_summary": final_result.final_output[:1000],
                    "assumptions": ["Unable to parse full plan structure"]
                }
        
        pdf_path = generate_event_proposal_pdf(
            event_details=event_details,
            final_plan=final_plan_dict,
            specialist_outputs=specialist_outputs
        )
        
        print(f"✅ PDF report generated: {pdf_path}\n")
        pdf_generated = True
        
    except Exception as e:
        print(f"⚠️  PDF generation error: {e}\n")
        pdf_path = None
        pdf_generated = False
    
    # Return comprehensive results
    return {
        "event_details": event_details,
        "planning_phase": planning_result.final_output,
        "specialist_outputs": specialist_outputs,
        "final_plan": final_result.final_output,
        "calendar_invite": calendar_result.final_output,
        "registration_form": form_data,
        "pdf_report": pdf_path,
        "agents_used": required_agents + ["calendar", "form"],
        "success": True,
        "pdf_generated": pdf_generated
    }


