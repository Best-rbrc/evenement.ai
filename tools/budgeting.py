from typing import Dict, List, Any

def create_budget_breakdown(event_details: Dict[str, Any], required_agents: List[str]) -> Dict[str, Any]:
    """Create a budget breakdown based on event details and required agents."""
    
    budget_categories = {}
    
    # Base budget allocation percentages by event type
    event_type = event_details.get("event_type", "").lower()
    
    if "wedding" in event_type:
        budget_categories = {
            "venue": 0.40,
            "catering": 0.30,
            "decoration": 0.15,
            "photography": 0.10,
            "music": 0.05
        }
    elif "conference" in event_type or "corporate" in event_type:
        budget_categories = {
            "venue": 0.35,
            "catering": 0.25,
            "speakers": 0.20,
            "communication": 0.10,
            "programme": 0.10
        }
    elif "tech" in event_type:
        budget_categories = {
            "venue": 0.30,
            "catering": 0.20,
            "speakers": 0.25,
            "programme": 0.15,
            "communication": 0.10
        }
    else:
        # Default allocation
        budget_categories = {
            "venue": 0.30,
            "catering": 0.25,
            "communication": 0.20,
            "programme": 0.15,
            "other": 0.10
        }
    
    # Adjust based on available agents
    available_agents = [agent for agent in required_agents if agent in budget_categories]
    
    if available_agents:
        # Redistribute budget among available agents
        total_allocation = sum(budget_categories.get(agent, 0) for agent in available_agents)
        if total_allocation > 0:
            for agent in available_agents:
                budget_categories[agent] = budget_categories.get(agent, 0) / total_allocation
    
    return budget_categories
