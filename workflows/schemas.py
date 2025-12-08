"""Canonical JSON schemas for agent outputs.

Agents MUST return outputs matching these exact structures.
"""
import json
import re
from typing import Dict, Any


# Canonical JSON schemas - agents MUST return outputs matching these exact structures
AGENT_SCHEMAS = {
    "planning": {
        "analysis": "string",
        "required_agents": ["venue", "catering", "programme", "speakers", "communication", "activities", "entertainment", "budgeting", "scheduling", "calendar", "form", "logo"],
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
    "logo": {
        "status": "success|error",
        "logo_file_path": "string",
        "logo_url": "string",
        "design_rationale": "string",
        "color_palette": "string",
        "typography_suggestions": "string",
        "usage_guidelines": ["string"],
        "branding_recommendations": ["string"],
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

