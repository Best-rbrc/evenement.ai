from typing import Dict, List, Any

def create_risk_assessment(event_details: Dict[str, Any], required_agents: List[str]) -> Dict[str, List[str]]:
    """Create a risk assessment based on event details and required agents."""
    
    risks = {
        "high_risk": [],
        "medium_risk": [],
        "low_risk": []
    }
    
    # Common risks for all events
    risks["high_risk"].extend([
        "Weather issues (for outdoor events)",
        "Venue availability changes",
        "Key speaker cancellations"
    ])
    
    risks["medium_risk"].extend([
        "Catering delivery issues",
        "Technical equipment failures",
        "Transportation delays"
    ])
    
    risks["low_risk"].extend([
        "Minor schedule adjustments",
        "Small attendance variations",
        "Decoration timing issues"
    ])
    
    # Event-specific risks
    event_type = event_details.get("event_type", "").lower()
    
    if "wedding" in event_type:
        risks["high_risk"].append("Vendor no-shows")
        risks["medium_risk"].append("Guest count changes")
    
    elif "conference" in event_type:
        risks["high_risk"].append("Speaker cancellations")
        risks["medium_risk"].append("Registration system issues")
    
    elif "tech" in event_type:
        risks["high_risk"].append("Technical demo failures")
        risks["medium_risk"].append("Internet connectivity issues")
    
    return risks
