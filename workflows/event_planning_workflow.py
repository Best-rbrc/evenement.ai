
from typing import Dict, Any, List
import asyncio

def infer_required_agents(event_details: Dict[str, Any]) -> List[str]:
    """Infer a conservative list of specialized agents to involve.

    This is intentionally simple; it can be extended later with rules.
    """
    base = [
        "venue",
        "catering",
        "programme",
        "speakers",
        "communication",
        "registration",
        "activities",
        "entertainment",
    ]

    etype = str(event_details.get("event_type", "in_person")).lower()
    if etype in ("virtual", "online"):
        # virtual events don't need physical venue/catering
        base = [b for b in base if b not in ("venue", "catering")]

    # allow override from caller
    explicit = event_details.get("required_agents")
    if isinstance(explicit, list) and explicit:
        # normalize to lowercase
        normalized = [str(x).lower() for x in explicit]
        return normalized

    return base


def run_event_planning(event_details: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous entrypoint used by `app.py`.

    1. Infer or read required agents
    2. Create specialized agents
    3. Create a Coordinator agent that will run the iterative orchestration
    4. Run the async `produce_actionable_plan` and return the result dict
    """
    required_agents = infer_required_agents(event_details)

    # Delay importing custom_agents factories until runtime so the module can
    # be imported in environments without the full SDK installed.
    try:
        from custom_agents.base import create_specialized_agents
        from custom_agents.coordinator_agent import create_coordinator_agent
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError("Required custom_agents package failed to import: %s" % exc)

    # Create specialized agents (factories live in custom_agents/*)
    specialized_agents = create_specialized_agents(required_agents)

    # Build a Coordinator agent to synthesize and manage handoffs
    coordinator = create_coordinator_agent(event_details, required_agents, specialized_agents)

    # Import the heavy plan generation implementation here to avoid import
    # failures at module import time when the SDK is unavailable.
    try:
        from workflows.plan_generation import produce_actionable_plan
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError("Required plan_generation module failed to import: %s" % exc)

    # Delegate to the async plan-generation function
    try:
        result = asyncio.run(produce_actionable_plan(coordinator, event_details, required_agents))
    except RuntimeError:
        # If an event loop is already running (e.g., in some test harnesses),
        # create a new loop and run it there.
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(produce_actionable_plan(coordinator, event_details, required_agents))
        finally:
            asyncio.set_event_loop(None)

    return result
