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
import shutil
from pathlib import Path

# Allow longer agent exchanges (default 10 can be too short for tool-rich agents)
AGENT_MAX_TURNS = 20

# Sandboxed MCP configuration
SANDBOX_DIR = Path("/tmp/mcp_event_outputs")
PROJECT_OUTPUT_DIR = Path(__file__).parent.parent / "event_outputs"
SANDBOX_ENABLED = False  # Set to False to disable sandboxing

# Canonical JSON schemas - agents MUST return outputs matching these exact structures
AGENT_SCHEMAS = {
    "planning": {
        "analysis": "string",
        "required_agents": ["venue", "catering", "programme", "speakers", "communication", "activities", "entertainment", "budgeting", "scheduling", "calendar", "form"],
        "execution_order_rationale": "string",
        "special_considerations": ["string"],
    },
    "budgeting": {
        "budget_allocation_recommended": {"category": {"recommended_spend": "number", "pct_of_total": "number", "notes": "string"}},
        "major_category_breakdowns": {"category": {"recommended_spend": "number", "pct_of_total": "number", "key_assumptions": ["string"]}},
        "what_if_scenarios": [{"name": "string", "delta": "string", "impact": "string", "recommendation": "string"}],
        "scenario_recommendation": {"name": "string", "reason": "string"},
        "allocation_rationale": "string",
        "warnings": ["string"],
    },
    "venue": {
        "summary": "string",
        "venues": [{"name": "string", "location": "string", "capacity": "number", "estimated_cost": "string|number", "amenities": ["string"], "availability_notes": "string", "website": "string", "backup_alternatives": ["string"]}],
        "timeline_and_logistics": ["string"],
        "top_recommendation": {"option": "string", "rationale": "string", "dependencies": ["string"]},
    },
    "catering": {
        "summary": "string",
        "menu_overview": ["string"],
        "dietary_accommodations": ["string"],
        "budget_estimate": {"per_person": "number", "total": "number", "notes": "string"},
        "timeline_and_logistics": ["string"],
    },
    "programme": {
        "summary": "string",
        "programme_recommendations": {
            "options": [{"name": "string", "description": "string", "capacity": "string|number", "cost": "string|number", "amenities": ["string"], "dependencies": ["string"]}],
            "timeline_and_logistics": ["string"],
            "session_and_flow": {"key": "time-range-or-note"},
            "breaks_networking": ["string"],
            "technical_and_materials_requirements": ["string"],
            "contingency_plans": ["string"],
            "top_recommendation": {"option": "string", "rationale": "string", "dependencies": "string"},
            "backup_option": {"option": "string", "rationale": "string"},
        },
        "next_steps": ["string"],
    },
    "speakers": {
        "summary": "string",
        "speakers_recommendations": {
            "primary_objectives": ["string"],
            "top_speaker_options": [{"name": "string", "bio": "string", "estimated_fee": "string|number", "ideal_role": "string", "logistics": "string", "rationale": "string"}],
            "honorarium_budget_itemization": {"item": "string|number"},
            "timeline_logistics": ["string"],
            "technical_dependencies": ["string"],
            "other_dependencies": ["string"],
            "backup_plan": {"virtual_alternative": "string", "local_rising_star": "string"},
        },
        "recommendation_rationale": "string",
    },
    "activities": {
        "activity_planning": {
            "summary": "string",
            "recommendations": [{"name": "string", "description": "string", "duration": "string|number", "cost_estimate": "string|number", "notes": "string"}],
            "logistics": ["string"],
            "budget_estimate": {"total": "number", "breakdown": {"item": "number"}},
        }
    },
    "entertainment": {
        "entertainment_recommendations": {
            "summary": "string",
            "specific_options": [{"name": "string", "description": "string", "cost_estimate": "number", "vendor_notes": "string"}],
            "budget_estimate": {"total": "number", "breakdown": {"item": "number"}},
            "recommended_package": {"option": "string", "components": ["string"], "rationale": ["string"]},
            "timeline_and_logistics": ["string"],
            "technical_requirements": ["string"],
            "backup_entertainment_plans": [{"scenario": "string", "plan": "string"}],
            "dependencies_on_other_areas": ["string"],
            "top_recommendations_and_rationale": {
                "recommendation_1": {"choice": "string", "reason": "string"},
                "recommendation_2": {"choice": "string", "reason": "string"},
            },
        }
    },
    "communication": {
        "communication_recommendations": {
            "overview": "string",
            "channels": ["string"],
            "key_messages": ["string"],
            "timeline": ["string"],
            "budget_overview": {"total": "number", "breakdown": {"channel": "number"}},
        }
    },
    "scheduling": {
        "status": "optimal|feasible|infeasible",
        "optimized_schedule": [{"session_id": "number", "name": "string", "start_time": "HH:MM", "end_time": "HH:MM", "duration": "number", "room": "string", "capacity": "number", "speaker": "string", "expected_attendees": "number"}],
        "metrics": {"total_duration": "number", "event_ends_at": "HH:MM", "room_utilization": {"room": "pct"}, "conflicts_resolved": "string"},
        "conflicts_explained": ["string"],
        "actionable_suggestions": ["string"],
        "next_steps": ["string"],
    },
    "calendar": {
        "calendar_file_path": "string",
        "event_summary": "string",
        "timing_details": "string",
        "import_instructions": "string",
    },
    "form": {
        "form_url": "string",
        "status": "success|error",
        "message": "string|null",
    },
    "final_plan": {
        "executive_summary": "string",
        "timeline": [{"phase": "string", "tasks": ["string"], "deadline": "YYYY-MM-DD"}],
        "schedule": {
            "optimized": "boolean",
            "sessions": [{"session_id": "number", "name": "string", "start_time": "HH:MM", "end_time": "HH:MM", "duration": "number", "room": "string", "capacity": "number", "speaker": "string", "expected_attendees": "number"}],
            "metrics": {"total_duration": "string|number", "event_ends_at": "HH:MM", "room_utilization": {"room": "pct"}, "conflicts_resolved": "string"},
            "status": "optimal|feasible|infeasible",
        },
        "budget": {"total_available": "number", "total_allocated": "number", "by_category": {"category": "number"}, "status": "within_budget|over_budget|at_limit"},
        "recommendations": {"venue": {}, "catering": {}, "programme": {}, "speakers": {}, "communication": {}, "activities": {}, "entertainment": {}, "budgeting": {}, "scheduling": {}},
        "risks": [{"risk": "string", "severity": "high|medium|low", "mitigation": "string"}],
        "action_items": [{"action": "string", "owner": "string", "deadline": "string", "priority": "high|medium|low"}],
        "assumptions": ["string"],
    },
}


def validate_agent_output(agent_name: str, output: Any) -> Dict[str, Any]:
    """Validate and normalize agent output to match canonical schema.
    
    Args:
        agent_name: The agent identifier (e.g., 'venue', 'budgeting', 'final_plan')
        output: Raw output from the agent (string or dict)
    
    Returns:
        Validated dict matching the canonical schema
    
    Raises:
        ValueError: If output cannot be parsed or validated
    """
    # Parse if string - try multiple extraction methods
    if isinstance(output, str):
        output_str = output.strip()
        
        # Try direct JSON parse first
        try:
            parsed = json.loads(output_str)
            output = parsed
        except json.JSONDecodeError:
            # Try extracting JSON from markdown code blocks
            try:
                # Try ```json ... ``` blocks
                if '```json' in output_str:
                    json_str = output_str.split('```json')[1].split('```')[0].strip()
                elif '```' in output_str:
                    json_str = output_str.split('```')[1].split('```')[0].strip()
                else:
                    # Try to find JSON object {...}
                    import re
                    match = re.search(r'\{.*\}', output_str, re.DOTALL)
                    if not match:
                        raise ValueError(f"No JSON object found in output")
                    json_str = match.group(0)
                
                parsed = json.loads(json_str)
                output = parsed
            except (json.JSONDecodeError, IndexError, ValueError) as e:
                raise ValueError(f"Agent '{agent_name}' returned invalid JSON: {e}")
    
    if not isinstance(output, dict):
        raise ValueError(f"Agent '{agent_name}' must return a dict, got {type(output)}")
    
    schema = AGENT_SCHEMAS.get(agent_name)
    if not schema:
        # If no schema defined, return as-is (for backward compatibility)
        return output
    
    # Ensure all required top-level keys exist
    missing_keys = [key for key in schema.keys() if key not in output]
    if missing_keys:
        raise ValueError(f"Agent '{agent_name}' missing required keys: {', '.join(missing_keys)}")
    
    return output


def get_current_date_context() -> str:
    """Get current date context for agents."""
    current_date = datetime.datetime.now()
    return f"Today's date: {current_date.strftime('%B %d, %Y')} ({current_date.strftime('%Y-%m-%d')})"


async def setup_sandboxed_mcp():
    """Setup sandboxed MCP server for file operations.
    
    Returns:
        MCPServers instance (not a context manager, just stores the servers)
    """
    from mcp_sandbox_openai_sdk import (
        FSAccess,
        MCPManifest,
        Permission,
        SandboxedMCPStdio,
    )
    
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    PROJECT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    manifest = MCPManifest(
        name="Filesystem Server",
        description="Sandbox-restricted file server for event outputs (ICS calendar files)",
        registry="npm",
        package_name="@modelcontextprotocol/server-filesystem",
        permissions=[
            Permission.MCP_AC_FILESYSTEM_READ,
            Permission.MCP_AC_FILESYSTEM_WRITE,
            Permission.MCP_AC_FILESYSTEM_DELETE,
        ],
    )
    
    # Create sandboxed MCP server
    sandboxed_server = SandboxedMCPStdio(
        manifest=manifest,
        runtime_args=[str(SANDBOX_DIR)],
        runtime_permissions=[
            FSAccess(str(SANDBOX_DIR), read=True, write=True),
        ],
    )
    
    # Initialize the server
    await sandboxed_server.__aenter__()
    return sandboxed_server


def copy_sandbox_files_to_project():
    """Copy files from sandbox temp directory to project directory."""
    if not SANDBOX_DIR.exists():
        return
    
    copied_count = 0
    for file in SANDBOX_DIR.glob("*"):
        if file.is_file():
            dest = PROJECT_OUTPUT_DIR / file.name
            shutil.copy2(file, dest)
            copied_count += 1
    
    if copied_count > 0:
        print(f"✅ Copied {copied_count} file(s) from sandbox to {PROJECT_OUTPUT_DIR}")


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
    # Create ONE loop and use it throughout the workflow
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

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

    # Setup sandboxed MCP if enabled (before creating agents that need it)
    mcp_servers = None
    global SANDBOX_ENABLED
    if SANDBOX_ENABLED:
        try:
            print("🔒 Setting up sandboxed file server...\n")
            # Use the active event loop to setup MCP
            mcp_servers = loop.run_until_complete(setup_sandboxed_mcp())
            print("✅ MCP server initialized - calendar files will be sandboxed\n")
        except Exception as e:
            print(f"⚠️  MCP setup failed: {e}\n")
            print("⏸️  Falling back to local file writes (no sandboxing)\n")
            SANDBOX_ENABLED = False
            mcp_servers = None

    # Create all available specialists (coordinator will decide which to use)
    all_agent_types = [
        "venue", "catering", "programme", "speakers", 
        "communication", "activities", "entertainment", "budgeting", "scheduling", "calendar", "form"
    ]
    all_specialists = create_specialized_agents(all_agent_types, mcp_servers=mcp_servers if SANDBOX_ENABLED else None)
    
    if mcp_servers is not None:
        print("📡 Calendar agent configured with MCP servers\n")
    else:
        print("📂 Calendar agent using local file I/O\n")
    
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
    # Event loop is already set up at function start
    def _run_sync_with_backoff(agent, prompt, max_retries: int = 3):
        import time, re, random
        last_exc = None
        for attempt in range(max_retries):
            try:
                return Runner.run_sync(agent, prompt, max_turns=AGENT_MAX_TURNS)
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

        result = Runner.run_sync(agent, specialist_prompt, max_turns=AGENT_MAX_TURNS)
        
        # Validate and normalize output to match schema
        try:
            validated_output = validate_agent_output(agent_name, result.final_output)
            specialist_outputs[agent_name] = validated_output
        except ValueError as e:
            print(f"⚠️  Schema validation error for {agent_name}: {e}")
            print(f"   Storing raw output anyway for debugging...")
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

    calendar_result = Runner.run_sync(calendar_agent, calendar_prompt, max_turns=AGENT_MAX_TURNS)
    
    print("✅ Calendar invite generated!\n")
    
    # Create registration form
    print("Creating event registration form...\n")
    
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
    # Registration form will be auto-generated in Phase 4
    if "programme" in specialist_outputs:
        minimal_context["programme"] = "optional session preferences"

    form_prompt = (
        f"Create an RSVP/registration form for '{event_details.get('event_name')}'.\n\n"
        f"Essentials: {json.dumps(concise_event, indent=2)}\n\n"
        f"Guidelines: {json.dumps(minimal_context, indent=2)}\n\n"
        "Return ONLY valid JSON with: {\"form_url\": \"https://tally.so/r/xxxxx\", \"status\": \"success\"}."
    )

    # Create the form via shared helper (handles retries/backoff)
    from custom_agents.form_agent import extract_form_url_from_output, run_form_with_retries

    form_result, form_error = run_form_with_retries(form_prompt)

    # Extract form URL from output; on failure, surface the error instead of generating a local fallback
    form_data = extract_form_url_from_output(form_result.final_output if form_result else "")

    if form_data.get("status") == "success":
        print(f"✅ Registration form created: {form_data.get('form_url')}\n")
    else:
        error_message = form_error or form_data.get("message") or "Unknown error during form creation"
        print(f"⚠️  Remote form creation failed. Error: {error_message}\n")
        form_data = {
            "status": "error",
            "message": error_message,
            "raw_output": form_data.get("raw_output")
        }
    
    # ============================================================
    # PHASE 5: PDF REPORT GENERATION
    # ============================================================
    print(f"\n{'='*60}")
    print("📄 PHASE 5: Generating Professional PDF Report")
    print(f"{'='*60}\n")
    
    print("Creating comprehensive PDF proposal...\n")
    
    try:
        from tools.report_generator import generate_event_proposal_pdf
        
        # Validate final plan against schema
        try:
            final_plan_dict = validate_agent_output("final_plan", final_result.final_output)
        except ValueError as e:
            print(f"⚠️  Final plan schema validation error: {e}")
            print(f"   Using raw output for PDF generation...")
            final_plan_dict = final_result.final_output
            if isinstance(final_plan_dict, str):
                try:
                    final_plan_dict = json.loads(final_plan_dict)
                except:
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
    
    # ============================================================
    # PHASE 6: SMS NOTIFICATION (OPTIONAL)
    # ============================================================
    print(f"\n{'='*60}")
    print("📱 PHASE 6: SMS Notification")
    print(f"{'='*60}\n")
    
    # Ask user if they want to send SMS
    try:
        send_sms = input("Do you want to send event details via SMS (costs 1$ per sms and we only have 7$ left so please use responsiibily)? (yes/no): ").lower().strip()
        
        if send_sms in ['yes', 'y', 'true', '1']:
            print("Sending SMS notification...\n")
            
            try:
                from twilio.rest import Client
                
                # Twilio credentials
                account_sid = 'ACad1d89daf3c3b29db84f0714eeadb6cb'
                auth_token = '2a20c86b0ed50623d61b9404f85a6281'
                client = Client(account_sid, auth_token)
                
                # Create SMS body with Tally form
                event_name = event_details.get('event_name', 'Event')
                event_date = event_details.get('event_date', 'TBD')
                form_url = form_data.get('form_url', 'Form link available soon')
                
                sms_body = f"Hey! You're invited to {event_name} on {event_date}. RSVP: {form_url}"
                
                # Send SMS
                message = client.messages.create(
                    from_='+15075955374',
                    body=sms_body,
                    to='+41784018164'
                )
                
                print(f"✅ SMS sent successfully! Message SID: {message.sid}\n")
                sms_sent = True
                sms_message_sid = message.sid
                
            except Exception as sms_error:
                print(f"⚠️  Failed to send SMS: {sms_error}\n")
                sms_sent = False
                sms_message_sid = None
        else:
            print("SMS notification skipped.\n")
            sms_sent = False
            sms_message_sid = None
            
    except Exception as e:
        print(f"⚠️  SMS input error: {e}\n")
        sms_sent = False
        sms_message_sid = None
    
    # Validate planning phase output
    validated_planning = planning_result.final_output
    try:
        validated_planning = validate_agent_output("planning", planning_result.final_output)
    except ValueError as e:
        print(f"⚠️  Planning phase schema validation error: {e}")
    
    # Validate all specialist outputs one more time before returning
    validated_specialist_outputs = {}
    for agent_name, output in specialist_outputs.items():
        try:
            validated_specialist_outputs[agent_name] = validate_agent_output(agent_name, output)
        except ValueError as e:
            print(f"⚠️  Final validation error for {agent_name}: {e}")
            validated_specialist_outputs[agent_name] = output
    
    # Return comprehensive results
    result = {
        "event_details": event_details,
        "planning_phase": validated_planning,
        "specialist_outputs": validated_specialist_outputs,
        "final_plan": final_result.final_output,
        "calendar_invite": calendar_result.final_output,
        "registration_form": form_data,
        "pdf_report": pdf_path,
        "agents_used": required_agents + ["calendar", "form"],
        "success": True,
        "pdf_generated": pdf_generated,
        "sms_sent": sms_sent,
        "sms_message_sid": sms_message_sid
    }
    
    # Cleanup: close MCP and copy files
    try:
        if mcp_servers is not None:
            # MCPServers has async exit, but we can't await in sync context
            # Just let it be garbage collected; the sandboxed server will close
            print("\n🔒 Sandboxed file server closed.")
        
        if SANDBOX_ENABLED and SANDBOX_DIR.exists():
            print("📁 Copying files from sandbox to project...")
            copy_sandbox_files_to_project()
            print("✅ Sandbox files copied to event_outputs/\n")
    except Exception as cleanup_error:
        print(f"⚠️  Cleanup error: {cleanup_error}")
    
    # Show where calendar file was created
    from pathlib import Path
    calendar_files = list(Path("event_outputs").glob("*.ics"))
    if calendar_files:
        print("=" * 60)
        print("📅 Calendar Files Created:")
        for cf in calendar_files:
            if mcp_servers is not None:
                print(f"  📡 {cf.name} (via sandboxed MCP)")
            else:
                print(f"  📂 {cf.name} (local file I/O)")
        print("=" * 60 + "\n")
    
    return result


