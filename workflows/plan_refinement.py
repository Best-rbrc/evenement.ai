"""Plan refinement workflow for chat-based plan updates.

This module handles incremental updates to an existing event plan based on user requests.
Only the necessary agents are called, and changes are merged into the existing plan.
"""
from typing import Dict, Any, List
import json
import logging

from pydantic import BaseModel
from workflows.prompts import build_refinement_prompt, build_specialist_prompt, build_finalization_prompt
from workflows.workflow_utils import run_sync_with_backoff
from custom_agents.base import create_specialized_agents
from custom_agents.coordinator_agent import create_coordinator_agent

# Allow longer agent exchanges
AGENT_MAX_TURNS = 20

logger = logging.getLogger(__name__)


def to_dict(obj: Any) -> Any:
    """Convert Pydantic models to dicts, recursively."""
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    elif isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_dict(item) for item in obj]
    return obj


def refine_event_plan(
    current_plan: Dict[str, Any],
    specialist_outputs: Dict[str, Any],
    user_message: str,
    event_details: Dict[str, Any],
    required_agents: List[str]
) -> Dict[str, Any]:
    """Refine an existing event plan based on user request.
    
    Args:
        current_plan: Current final_plan dict
        specialist_outputs: Current specialist outputs dict
        user_message: User's chat message requesting changes
        event_details: Original event details
        required_agents: List of agents that were originally used
        
    Returns:
        Dict with:
            - updated_plan: New final_plan
            - changed_sections: List of sections that changed
            - agents_called: List of agents that were called
            - coordinator_message: Message from coordinator explaining changes
    """
    logger.info("="*80)
    logger.info("Starting Plan Refinement")
    logger.info(f"User request: {user_message}")
    logger.info(f"Event: {event_details.get('event_name', 'Unknown')}")
    logger.info("="*80)
    
    try:
        from agents import Runner
    except Exception as exc:
        raise RuntimeError(f"Required imports failed: {exc}")
    
    # Create all specialized agents
    all_agent_types = ["venue", "catering", "programme", "speakers", "activities", 
                       "entertainment", "communication", "budgeting", "scheduling"]
    
    all_specialists = create_specialized_agents(all_agent_types)
    
    # Create coordinator with handoffs to all specialists
    coordinator = create_coordinator_agent(event_details, all_agent_types, all_specialists)
    
    # Directly infer which agents to call from user message (faster than coordinator analysis)
    logger.info("Analyzing user request to determine which agents to call...")
    agents_to_call = []
    coordinator_message = ""
    
    # Infer agents from user message (much faster than coordinator analysis)
    user_lower = user_message.lower()
    if "venue" in user_lower or "location" in user_lower:
        agents_to_call.append("venue")
    if "catering" in user_lower or "food" in user_lower or "menu" in user_lower:
        agents_to_call.append("catering")
    if "budget" in user_lower or "cost" in user_lower or "cheaper" in user_lower or "expensive" in user_lower:
        agents_to_call.append("budgeting")
    if "schedule" in user_lower or "time" in user_lower or "session" in user_lower:
        agents_to_call.append("scheduling")
    if "speaker" in user_lower:
        agents_to_call.append("speakers")
    if "activity" in user_lower:
        agents_to_call.append("activities")
    if "entertainment" in user_lower:
        agents_to_call.append("entertainment")
    if "communication" in user_lower or "marketing" in user_lower:
        agents_to_call.append("communication")
    if "programme" in user_lower or "program" in user_lower:
        agents_to_call.append("programme")
    
    # Remove duplicates
    agents_to_call = list(set(agents_to_call))
    logger.info(f"Inferred agents to call from user message: {agents_to_call}")
    
    # If still no agents, return error
    if not agents_to_call:
        logger.warning("No agents determined from user message")
        return {
            "updated_plan": current_plan,
            "changed_sections": [],
            "agents_called": [],
            "coordinator_message": "I couldn't determine which aspects of the plan need to be changed. Could you be more specific? For example: 'change the venue', 'find different speakers', 'update the budget'.",
            "error": "No agents determined for refinement"
        }
    
    coordinator_message = f"Updating {', '.join(agents_to_call)} based on your request: {user_message}"
    
    # Call the necessary agents
    updated_outputs = specialist_outputs.copy()
    changed_sections = []
    
    for idx, agent_name in enumerate(agents_to_call, 1):
        if agent_name not in all_specialists:
            logger.warning(f"Agent {agent_name} not found in specialists, skipping")
            continue
        
        logger.info(f"[{idx}/{len(agents_to_call)}] Calling {agent_name} agent for refinement...")
        print(f"[{idx}/{len(agents_to_call)}]  Updating {agent_name}...")
        
        # Build specialist prompt with user's request and current context
        specialist_prompt = build_specialist_prompt(
            agent_name=agent_name,
            event_details=event_details,
            context=f"USER REQUEST: {user_message}\n\nCURRENT OUTPUT: {json.dumps(specialist_outputs.get(agent_name, {}), indent=2)}",
            specialist_outputs=specialist_outputs,
            required_agents=required_agents
        )
        
        # Run the agent with reduced max_turns for faster response
        agent = all_specialists[agent_name]
        try:
            result = run_sync_with_backoff(agent, specialist_prompt, max_turns=10)  # Reduced from 20
            
            # Convert Pydantic model to dict for JSON serialization
            updated_outputs[agent_name] = to_dict(result.final_output)
            changed_sections.append(agent_name)
            logger.info(f" {agent_name} agent updated successfully")
            print(f"    {agent_name} updated")
        except Exception as e:
            logger.error(f" Error updating {agent_name}: {e}")
            print(f"     {agent_name} update failed: {e}")
            # Keep existing output if update fails
            continue
    
    # If budget was affected, might need to update budgeting
    if any(agent in agents_to_call for agent in ["venue", "catering", "entertainment", "activities"]):
        if "budgeting" not in agents_to_call:
            logger.info("Cost-affecting agents were updated, calling budgeting agent to validate...")
            # Call budgeting agent to validate new costs
            budgeting_prompt = build_specialist_prompt(
                agent_name="budgeting",
                event_details=event_details,
                context=f"Some costs have changed. Please validate the budget with updated costs.",
                specialist_outputs=updated_outputs,
                required_agents=required_agents
            )
            budgeting_agent = all_specialists["budgeting"]
            budgeting_result = run_sync_with_backoff(budgeting_agent, budgeting_prompt, max_turns=AGENT_MAX_TURNS)
            # Convert Pydantic model to dict for JSON serialization
            updated_outputs["budgeting"] = to_dict(budgeting_result.final_output)
            if "budgeting" not in changed_sections:
                changed_sections.append("budgeting")
    
    # Regenerate final plan with updated outputs
    logger.info("Regenerating final plan with updated outputs...")
    print(" Regenerating final plan...")
    
    # Update required_agents to include any new agents that were called
    updated_required_agents = list(set(required_agents + agents_to_call))
    
    finalization_prompt = build_finalization_prompt(
        event_details=event_details,
        required_agents=updated_required_agents,
        specialist_outputs=updated_outputs
    )
    
    try:
        final_result = run_sync_with_backoff(coordinator, finalization_prompt, max_turns=15)  # Reduced from 20
        
        # Convert Pydantic model to dict for JSON serialization
        updated_plan = to_dict(final_result.final_output)
        logger.info(" Final plan regenerated successfully")
        print(" Final plan regenerated")
    except Exception as e:
        logger.error(f" Error regenerating final plan: {e}")
        print(f"  Error regenerating plan: {e}")
        # Fallback: merge changes into current plan
        updated_plan = current_plan.copy()
        if "recommendations" not in updated_plan:
            updated_plan["recommendations"] = {}
        for agent_name in changed_sections:
            if agent_name in updated_outputs:
                updated_plan["recommendations"][agent_name] = updated_outputs[agent_name]
    
    return {
        "updated_plan": updated_plan,
        "changed_sections": changed_sections,
        "agents_called": agents_to_call,
        "coordinator_message": coordinator_message or f"Updated {', '.join(changed_sections)} based on your request."
    }

