"""Prompt building functions for event planning workflow.

All prompts are built as functions that take context and return formatted strings.
"""
import json
from typing import Dict, Any, List
from workflows.workflow_utils import get_current_date_context


def build_planning_prompt(event_details: Dict[str, Any]) -> str:
    """Build the Phase 1 planning prompt for the coordinator.
    
    Args:
        event_details: Event information dict
        
    Returns:
        Formatted prompt string
    """
    return f"""You are the Event Planning Coordinator analyzing requirements for "{event_details['event_name']}".

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


def build_specialist_prompt(
    agent_name: str,
    event_details: Dict[str, Any],
    context: str = "",
    specialist_outputs: Dict[str, Any] = None,
    required_agents: List[str] = None
) -> str:
    """Build a prompt for a specialist agent.
    
    Args:
        agent_name: Name of the specialist agent
        event_details: Event information dict
        context: Context from previous specialist outputs
        specialist_outputs: All previous specialist outputs
        required_agents: List of required agents for this event
        
    Returns:
        Formatted prompt string
    """
    if specialist_outputs is None:
        specialist_outputs = {}
    if required_agents is None:
        required_agents = []
    
    if agent_name == "budgeting":
        return f"""You are the Budgeting specialist for "{event_details['event_name']}", a {event_details['event_type']} event.

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
        return f"""You are the Advanced Scheduling specialist for "{event_details['event_name']}", a {event_details['event_type']} event.

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
        
        return f"""You are the {agent_name} specialist for "{event_details['event_name']}", a {event_details['event_type']} event.

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


def build_finalization_prompt(
    event_details: Dict[str, Any],
    required_agents: List[str],
    specialist_outputs: Dict[str, Any]
) -> str:
    """Build the Phase 3 finalization prompt for the coordinator.
    
    Args:
        event_details: Event information dict
        required_agents: List of agents that were used
        specialist_outputs: All specialist outputs
        
    Returns:
        Formatted prompt string
    """
    return f"""You are the Event Planning Coordinator finalizing the plan for "{event_details['event_name']}".

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
   - For multi-day events: Add "date": "YYYY-MM-DD" to each session based on event_date range
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
   - **EVENT SCHEDULE (MANDATORY)**: ALWAYS include a schedule section with sessions/timeline
     * If scheduling agent was used: Use their optimized schedule
     * If programme agent provided schedule: Use their daily_schedule or session_and_flow
     * If neither exists: Create a basic schedule based on event details (start time, duration, breaks)
     * For multi-day events: Include date for each session
     * Minimum: At least one session with start_time, end_time, and name
   - Detailed budget breakdown by category with totals
   - **ALL SPECIALIST RECOMMENDATIONS (CRITICAL)**: You MUST include COMPLETE data from ALL specialist agents in the "recommendations" section
   - Risk assessment with mitigation strategies
   - Prioritized action items with deadlines
   - Assumptions made

4. **CRITICAL: RECOMMENDATIONS SECTION MUST INCLUDE ALL SPECIALIST DATA**

The "recommendations" section is the SINGLE SOURCE OF TRUTH for the frontend. You MUST include the COMPLETE output from each specialist agent:

- "venue": Include the ENTIRE venue agent output (venues array, summary, top_recommendation, timeline_and_logistics)
- "catering": Include the ENTIRE catering agent output (menu_overview, dietary_accommodations, budget_estimate, summary, timeline_and_logistics)
- "programme": Include the ENTIRE programme agent output (programme_recommendations object with all fields)
- "speakers": Include the ENTIRE speakers agent output (speakers_recommendations object with top_speaker_options, etc.)
- "activities": Include the ENTIRE activities agent output (activity_planning object with recommendations, logistics, budget_estimate)
- "entertainment": Include the ENTIRE entertainment agent output (entertainment_recommendations object with all fields)
- "communication": Include the ENTIRE communication agent output (communication_recommendations object with overview, channels, key_messages, timeline, budget_overview)
- "budgeting": Include the ENTIRE budgeting agent output (budget_allocation_recommended, major_category_breakdowns, what_if_scenarios, etc.)
- "scheduling": Include the ENTIRE scheduling agent output (status, optimized_schedule, metrics, conflicts_explained, etc.)

DO NOT create simplified versions - copy the COMPLETE specialist outputs into recommendations. The frontend relies ONLY on final_plan.recommendations.

5. OUTPUT as valid JSON:
{{
  "executive_summary": "...",
  "timeline": [
    {{"phase": "Phase name (e.g., 'Pre-Event Planning', 'Event Execution', 'Post-Event')", "tasks": ["Task 1", "Task 2", ...], "deadline": "YYYY-MM-DD"}}
  ],
  "schedule": {{
    "optimized": true/false,  // true if scheduling agent was used, false otherwise
    "sessions": [  // REQUIRED - ALWAYS include at least one session. For multi-day events, include "date": "YYYY-MM-DD" for each session
      {{
        "session_id": 1,
        "name": "string",  // e.g., "Welcome & Opening", "Main Event", "Closing"
        "start_time": "HH:MM",  // REQUIRED
        "end_time": "HH:MM",  // REQUIRED
        "duration": number,  // in minutes
        "room": "string",  // optional
        "speaker": "string",  // optional
        "date": "YYYY-MM-DD"  // REQUIRED for multi-day events
      }}
    ],
    "metrics": {{  // Optional if scheduling agent was not used
      "total_duration": "...",
      "event_ends_at": "...",
      "room_utilization": {{}},
      "conflicts_resolved": "..."
    }},
    "status": "optimal | feasible | infeasible | basic"  // "basic" if created from event details without optimization
  }},
  "budget": {{
    "total_available": number,
    "total_allocated": number,
    "by_category": {{"venue": number, "catering": number, ...}},  // Simple dict: category -> amount
    "status": "within_budget | over_budget | at_limit"
  }},
  "recommendations": {{
    "venue": {{"summary": "...", "venues": [...], "timeline_and_logistics": [...], "top_recommendation": {{...}}}},  // COMPLETE venue agent output
    "catering": {{"summary": "...", "menu_overview": [...], "dietary_accommodations": [...], "budget_estimate": {{...}}, "timeline_and_logistics": [...]}},  // COMPLETE catering agent output
    "programme": {{"summary": "...", "programme_recommendations": {{...}}, "next_steps": [...]}},  // COMPLETE programme agent output
    "speakers": {{"summary": "...", "speakers_recommendations": {{...}}, "recommendation_rationale": "..."}},  // COMPLETE speakers agent output
    "activities": {{"activity_planning": {{...}}}},  // COMPLETE activities agent output
    "entertainment": {{"entertainment_recommendations": {{...}}}},  // COMPLETE entertainment agent output
    "communication": {{"communication_recommendations": {{...}}}},  // COMPLETE communication agent output
    "budgeting": {{"budget_allocation_recommended": {{...}}, "major_category_breakdowns": {{...}}, "what_if_scenarios": [...], ...}},  // COMPLETE budgeting agent output
    "scheduling": {{"status": "...", "optimized_schedule": [...], "metrics": {{...}}, ...}}  // COMPLETE scheduling agent output (if used)
  }},
  "risks": [
    {{"risk": "...", "severity": "high|medium|low", "mitigation": "..."}}
  ],
  "action_items": [
    {{"action": "...", "owner": "...", "deadline": "...", "priority": "high|medium|low"}}
  ],
  "assumptions": [...]
}}

Use handoffs if needed to refine or add information. Then provide your final synthesized plan.

REMEMBER: The frontend relies ONLY on final_plan.recommendations - include COMPLETE specialist data there."""


def build_calendar_prompt(
    event_details: Dict[str, Any],
    specialist_outputs: Dict[str, Any],
    final_result_output: str
) -> str:
    """Build the calendar generation prompt.
    
    Args:
        event_details: Event information dict
        specialist_outputs: All specialist outputs
        final_result_output: Final plan output string
        
    Returns:
        Formatted prompt string
    """
    return f"""You are the Calendar Specialist for "{event_details['event_name']}".

{get_current_date_context()}

Event Details:
{json.dumps(event_details, indent=2)}

All Planning Outputs:
{json.dumps(specialist_outputs, indent=2)}

Final Plan:
{final_result_output}

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


def build_form_prompt(
    event_details: Dict[str, Any],
    concise_event: Dict[str, Any],
    minimal_context: Dict[str, Any]
) -> str:
    """Build the form creation prompt.
    
    Args:
        event_details: Event information dict
        concise_event: Compact event details
        minimal_context: Minimal context from specialists
        
    Returns:
        Formatted prompt string
    """
    return (
        f"Create an RSVP/registration form for '{event_details.get('event_name')}'.\n\n"
        f"Essentials: {json.dumps(concise_event, indent=2)}\n\n"
        f"Guidelines: {json.dumps(minimal_context, indent=2)}\n\n"
        "Return ONLY valid JSON with: {\"form_url\": \"https://tally.so/r/xxxxx\", \"status\": \"success\"}."
    )


def build_logo_prompt(
    event_details: Dict[str, Any],
    specialist_outputs: Dict[str, Any],
    final_result_output: str
) -> str:
    """Build the logo generation prompt.
    
    Args:
        event_details: Event information dict
        specialist_outputs: All specialist outputs
        final_result_output: Final plan output string
        
    Returns:
        Formatted prompt string
    """
    return f"""You are the Logo Design Specialist for "{event_details['event_name']}".

{get_current_date_context()}

Event Details:
{json.dumps(event_details, indent=2)}

All Planning Outputs:
{json.dumps(specialist_outputs, indent=2)}

Final Plan:
{final_result_output}

Your task:
Generate a professional logo for this event using the generate_logo_image() function.

1. Extract event information:
   - Event name: {event_details.get('event_name')}
   - Event type: {event_details.get('event_type')}
   - Event description: {event_details.get('event_description', '')}
   - Style preferences: Consider the event type and target audience

2. Generate the logo:
   - Use generate_logo_image() with appropriate parameters
   - Ensure the logo has a transparent background
   - Create a design that represents the event's purpose and style

3. Provide design information:
   - Design rationale
   - Color palette
   - Typography suggestions
   - Usage guidelines
   - Branding recommendations

Output JSON with:
- status: "success" or "error"
- logo_file_path: path to the generated logo file
- logo_url: file URL
- design_rationale: explanation of design choices
- color_palette: color information
- typography_suggestions: font recommendations
- usage_guidelines: array of usage instructions
- branding_recommendations: array of branding tips"""


def build_refinement_prompt(
    event_details: Dict[str, Any],
    current_plan: Dict[str, Any],
    specialist_outputs: Dict[str, Any],
    user_message: str,
    required_agents: List[str]
) -> str:
    """Build the refinement prompt for the coordinator to analyze user requests.
    
    Args:
        event_details: Original event information dict
        current_plan: Current final_plan dict
        specialist_outputs: Current specialist outputs dict
        user_message: User's chat message requesting changes
        required_agents: List of agents that were originally used
        
    Returns:
        Formatted prompt string
    """
    return f"""You are the Event Planning Coordinator for "{event_details['event_name']}".

{get_current_date_context()}

The user has requested changes to the existing event plan. Your task is to:
1. Analyze the user's request to understand what needs to change
2. Determine which specialist agents need to be called to make those changes
3. Call ONLY the necessary agents (don't regenerate everything)
4. Merge the new agent outputs with the existing plan
5. Regenerate the final plan with the changes integrated

USER'S REQUEST:
"{user_message}"

CURRENT EVENT PLAN:
{json.dumps(current_plan, indent=2)}

CURRENT SPECIALIST OUTPUTS:
{json.dumps(specialist_outputs, indent=2)}

ORIGINAL EVENT DETAILS:
{json.dumps(event_details, indent=2)}

AGENTS ORIGINALLY USED:
{', '.join(required_agents)}

YOUR TASK:

1. ANALYZE the user's request:
   - What specific aspect needs to change? (venue, catering, budget, schedule, etc.)
   - Which agents are affected by this change?
   - Are there dependencies? (e.g., changing venue might affect catering or budget)

2. DETERMINE which agents to call:
   - Only call agents whose outputs need to change
   - Consider dependencies (e.g., venue change → might need budget update)
   - DO NOT call agents that aren't affected by the request

3. CALL the necessary agents:
   - Handoff to each affected agent with:
     * The user's specific request
     * Current context from existing outputs
     * Any constraints or requirements
   - Example: "User wants a cheaper venue. Current budget is $X. Find venues under $Y."

4. MERGE the new outputs:
   - Keep existing outputs from agents that weren't called
   - Replace outputs from agents that were called with their new outputs
   - Preserve data structure and completeness

5. REGENERATE the final plan:
   - Update the final_plan with new agent outputs
   - Ensure recommendations section includes ALL specialist data (both updated and unchanged)
   - Update executive_summary if major changes occurred
   - Update budget if costs changed
   - Update schedule if timing changed
   - Keep timeline, risks, and action_items current

CRITICAL REQUIREMENTS:
- Only change what the user requested - preserve everything else
- Ensure recommendations section includes COMPLETE outputs from ALL agents (both updated and unchanged)
- Maintain data structure consistency
- If budget changes, ensure budget section reflects new totals
- If schedule changes, ensure schedule section is updated

OUTPUT your analysis and actions as JSON:
{{
  "analysis": "What the user wants to change and which agents are affected",
  "agents_to_call": ["agent1", "agent2", ...],  // Only agents that need to update
  "reasoning": "Why these agents need to be called",
  "dependencies": ["agent1 affects agent2 because..."],  // If any
  "action": "I will now handoff to [agent names] to make these changes"
}}

After calling the agents, regenerate the final plan with the updated information."""

