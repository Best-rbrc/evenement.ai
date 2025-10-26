from orchestrator.orchestrator import Orchestrator, Step
from app_agents.planner_agent import planner_agent
from app_agents.budget_agent import budget_agent
from app_agents.venue_agent import venue_agent
from app_agents.invite_agent import invite_agent
from agents import Runner
import json

NAME_TO_AGENT = {
    "PlannerAgent": planner_agent,
    "BudgetAgent":  budget_agent,
    "VenueAgent":   venue_agent,
    "InviteAgent":  invite_agent,
}
ALLOWED = set(NAME_TO_AGENT.keys())

def run_event_planning_workflow(request):
    """
    Hybrid dynamic workflow:
    - PlannerAgent proposes steps (JSON)
    - We validate/adjust steps (business rules)
    - Orchestrator executes deterministically
    """
    city        = request.get("city", "Berlin")
    attendees   = int(request.get("attendees", 100))
    month       = request.get("month", "May")
    event_type  = request.get("event_type", "in_person")  # <-- important

    user_goal = (
        f"Plan an event for {attendees} people in {city} in {month}. "
        f"event_type={event_type}. "
        "Return ONLY JSON of the form: "
        '{"steps":[{"agent":"<AgentName>","input":"<Task>"}]}'
    )

    print(f"\n🧠 Asking PlannerAgent to design workflow for: {user_goal}\n")
    planner_run = Runner.run_sync(planner_agent, user_goal)

    # Parse JSON
    try:
        plan_json = json.loads(planner_run.final_output)
        steps_raw = plan_json.get("steps", [])
    except Exception:
        print("⚠️ PlannerAgent output was not valid JSON; using fallback plan.")
        steps_raw = [
            {"agent": "BudgetAgent", "input": "Estimate basic budget."},
            {"agent": "VenueAgent",  "input": f"Find venues in {city} for {attendees}."},
            {"agent": "InviteAgent", "input": "Draft short invitations with RSVP link."},
        ]

    # Hard rule: no venue for virtual events
    if event_type == "virtual":
        before = len(steps_raw)
        steps_raw = [s for s in steps_raw if s.get("agent") != "VenueAgent"]
        if len(steps_raw) != before:
            print("ℹ️ Removed VenueAgent step because event_type='virtual'.")

    # Keep only allowed agents + sane inputs
    chosen = [
        s for s in steps_raw
        if s.get("agent") in ALLOWED and isinstance(s.get("input"), str) and s["input"].strip()
    ]

    print("📋 PlannerAgent chose (after validation):")
    for i, s in enumerate(chosen, 1):
        print(f"  {i}. {s['agent']} — {s['input'][:90]}")

    steps: list[Step] = [(NAME_TO_AGENT[s["agent"]], s["input"]) for s in chosen]

    orchestrator = Orchestrator()
    result = orchestrator.execute(steps)

    print("\n✅ Finished executing all chosen agents.")
    return result