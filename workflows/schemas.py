"""Canonical JSON schemas for agent outputs.

Agents MUST return outputs matching these exact structures.
Detailed schemas with nested structures for proper validation.
"""
import json
import re
from typing import Dict, Any, List, Union, Tuple


# Type aliases for schema definitions
SchemaType = Union[type, Tuple[type, ...], Dict[str, Any], List[Any]]


# Detailed schemas with nested structures - can be validated recursively
AGENT_SCHEMAS = {
    "planning": {
        "analysis": str,
        "required_agents": list,
        "execution_order_rationale": str,
        "special_considerations": list,
    },
    "budgeting": {
        "budget_allocation_recommended": dict,  # {category: {recommended_spend: number, pct_of_total: number, notes: str}}
        "major_category_breakdowns": dict,  # {category: {recommended_spend: number, pct_of_total: number, key_assumptions: list}}
        "what_if_scenarios": {
            "type": list,
            "items": {
                "name": str,
                "delta": str,
                "impact": str,
                "recommendation": str,
            }
        },
        "scenario_recommendation": {
            "name": str,
            "reason": str,
        },
        "allocation_rationale": str,
        "warnings": list,
    },
    "venue": {
        "summary": str,
        "venues": {
            "type": list,
            "items": {
                "name": str,
                "location": str,
                "capacity": (int, float),
                "estimated_cost": (str, int, float),  # Can be string or number
                "amenities": list,
                "availability_notes": str,
                "website": str,  # Must be valid URL or empty string
                "backup_alternatives": list,
            }
        },
        "timeline_and_logistics": list,
        "top_recommendation": {
            "option": str,
            "rationale": str,
            "dependencies": list,
        },
    },
    "catering": {
        "summary": str,
        "menu_overview": list,
        "dietary_accommodations": list,
        "budget_estimate": {
            "per_person": (int, float),
            "total": (int, float),
            "notes": str,
        },
        "timeline_and_logistics": list,
    },
    "programme": {
        "summary": str,
        "programme_recommendations": {
            "options": {
                "type": list,
                "items": {
                    "name": str,
                    "description": str,
                    "capacity": (str, int, float),
                    "cost": (str, int, float),
                    "amenities": list,
                    "dependencies": list,
                }
            },
            "timeline_and_logistics": list,
            "session_and_flow": dict,  # {key: "time-range-or-note"}
            "breaks_networking": list,
            "technical_and_materials_requirements": list,
            "contingency_plans": list,
            "top_recommendation": {
                "option": str,
                "rationale": str,
                "dependencies": (str, list),  # Can be string or list
            },
            "backup_option": {
                "option": str,
                "rationale": str,
            },
        },
        "next_steps": list,
    },
    "speakers": {
        "summary": str,
        "speakers_recommendations": {
            "primary_objectives": list,
            "top_speaker_options": {
                "type": list,
                "items": {
                    "name": str,
                    "bio": str,
                    "estimated_fee": (str, int, float),
                    "ideal_role": str,
                    "logistics": str,
                    "rationale": str,
                    "company": str,  # Optional but recommended
                    "image": str,  # Optional
                }
            },
            "honorarium_budget_itemization": dict,  # {item: str|number}
            "timeline_logistics": list,
            "technical_dependencies": list,
            "other_dependencies": list,
            "backup_plan": {
                "virtual_alternative": str,
                "local_rising_star": str,
            },
        },
        "recommendation_rationale": str,
    },
    "activities": {
        "activity_planning": {
            "summary": str,
            "recommendations": {
                "type": list,
                "items": {
                    "name": str,
                    "description": str,
                    "duration": (str, int, float),
                    "cost_estimate": (str, int, float),
                    "notes": str,
                }
            },
            "logistics": list,
            "budget_estimate": {
                "total": (int, float),
                "breakdown": dict,  # {item: number}
            },
        },
    },
    "entertainment": {
        "entertainment_recommendations": {
            "summary": str,
            "specific_options": {
                "type": list,
                "items": {
                    "name": str,
                    "description": str,
                    "cost_estimate": (int, float),
                    "vendor_notes": str,
                }
            },
            "budget_estimate": {
                "total": (int, float),
                "breakdown": dict,  # {item: number}
            },
            "recommended_package": {
                "option": str,
                "components": list,
                "rationale": list,
            },
            "timeline_and_logistics": list,
            "technical_requirements": list,
            "backup_entertainment_plans": {
                "type": list,
                "items": {
                    "scenario": str,
                    "plan": str,
                }
            },
            "dependencies_on_other_areas": list,
            "top_recommendations_and_rationale": {
                "recommendation_1": {
                    "choice": str,
                    "reason": str,
                },
                "recommendation_2": {
                    "choice": str,
                    "reason": str,
                },
            },
        },
    },
    "communication": {
        "communication_recommendations": {
            "overview": str,
            "channels": list,
            "key_messages": list,
            "timeline": list,
            "budget_overview": {
                "total": (int, float),
                "breakdown": dict,  # {channel: number}
            },
        },
    },
    "scheduling": {
        "status": str,  # "optimal" | "feasible" | "infeasible"
        "optimized_schedule": {
            "type": list,
            "items": {
                "session_id": (int, float),
                "name": str,
                "start_time": str,  # HH:MM format
                "end_time": str,  # HH:MM format
                "duration": (int, float),
                "room": str,
                "capacity": (int, float),
                "speaker": str,
                "expected_attendees": (int, float),
                "date": str,  # Optional: YYYY-MM-DD for multi-day events
            }
        },
        "metrics": {
            "total_duration": (int, float, str),
            "event_ends_at": str,  # HH:MM format
            "room_utilization": dict,  # {room: "pct"}
            "conflicts_resolved": str,
        },
        "conflicts_explained": list,
        "actionable_suggestions": list,
        "next_steps": list,
    },
    "calendar": {
        "calendar_file_path": str,
        "event_summary": str,
        "timing_details": str,
        "import_instructions": str,
    },
    "form": {
        "form_url": str,
        "status": str,  # "success" | "error"
        "message": str,
    },
    "logo": {
        "status": str,  # "success" | "error"
        "logo_file_path": str,
        "logo_url": str,
        "design_rationale": str,
        "color_palette": str,
        "typography_suggestions": str,
        "usage_guidelines": list,
        "branding_recommendations": list,
    },
    "final_plan": {
        "executive_summary": str,
        "timeline": {
            "type": list,
            "items": {
                "phase": str,
                "tasks": list,
                "deadline": str,  # YYYY-MM-DD format
            }
        },
        "schedule": {
            "optimized": bool,
            "sessions": {
                "type": list,
                "items": {
                    "session_id": (int, float),
                    "name": str,
                    "start_time": str,  # HH:MM format
                    "end_time": str,  # HH:MM format
                    "duration": (int, float),
                    "room": str,
                    "capacity": (int, float),
                    "speaker": str,
                    "expected_attendees": (int, float),
                    "date": str,  # Optional: YYYY-MM-DD for multi-day events
                }
            },
            "metrics": dict,
            "status": str,  # "optimal" | "feasible" | "infeasible" | "basic"
        },
        "budget": {
            "total_available": (int, float),
            "total_allocated": (int, float),
            "by_category": dict,  # {category: number}
            "status": str,  # "within_budget" | "over_budget" | "at_limit"
        },
        "recommendations": {
            # All specialist outputs - each is optional but required if that agent was used
            "venue": {
                "summary": str,
                "venues": {
                    "type": list,
                    "items": {
                        "name": str,
                        "location": str,
                        "capacity": (int, float),
                        "estimated_cost": (str, int, float),
                        "amenities": list,
                        "availability_notes": str,
                        "website": str,
                        "backup_alternatives": list,
                    }
                },
                "timeline_and_logistics": list,
                "top_recommendation": {
                    "option": str,
                    "rationale": str,
                    "dependencies": list,
                },
            },
            "catering": {
                "summary": str,
                "menu_overview": list,
                "dietary_accommodations": list,
                "budget_estimate": {
                    "per_person": (int, float),
                    "total": (int, float),
                    "notes": str,
                },
                "timeline_and_logistics": list,
            },
            "programme": {
                "summary": str,
                "programme_recommendations": {
                    "options": {
                        "type": list,
                        "items": {
                            "name": str,
                            "description": str,
                            "capacity": (str, int, float),
                            "cost": (str, int, float),
                            "amenities": list,
                            "dependencies": list,
                        }
                    },
                    "timeline_and_logistics": list,
                    "session_and_flow": dict,
                    "breaks_networking": list,
                    "technical_and_materials_requirements": list,
                    "contingency_plans": list,
                    "top_recommendation": {
                        "option": str,
                        "rationale": str,
                        "dependencies": (str, list),
                    },
                    "backup_option": {
                        "option": str,
                        "rationale": str,
                    },
                },
                "next_steps": list,
            },
            "speakers": {
                "summary": str,
                "speakers_recommendations": {
                    "primary_objectives": list,
                    "top_speaker_options": {
                        "type": list,
                        "items": {
                            "name": str,
                            "bio": str,
                            "estimated_fee": (str, int, float),
                            "ideal_role": str,
                            "logistics": str,
                            "rationale": str,
                            "company": str,
                            "image": str,
                        }
                    },
                    "honorarium_budget_itemization": dict,
                    "timeline_logistics": list,
                    "technical_dependencies": list,
                    "other_dependencies": list,
                    "backup_plan": {
                        "virtual_alternative": str,
                        "local_rising_star": str,
                    },
                },
                "recommendation_rationale": str,
            },
            "activities": {
                "activity_planning": {
                    "summary": str,
                    "recommendations": {
                        "type": list,
                        "items": {
                            "name": str,
                            "description": str,
                            "duration": (str, int, float),
                            "cost_estimate": (str, int, float),
                            "notes": str,
                        }
                    },
                    "logistics": list,
                    "budget_estimate": {
                        "total": (int, float),
                        "breakdown": dict,
                    },
                },
            },
            "entertainment": {
                "entertainment_recommendations": {
                    "summary": str,
                    "specific_options": {
                        "type": list,
                        "items": {
                            "name": str,
                            "description": str,
                            "cost_estimate": (int, float),
                            "vendor_notes": str,
                        }
                    },
                    "budget_estimate": {
                        "total": (int, float),
                        "breakdown": dict,
                    },
                    "recommended_package": {
                        "option": str,
                        "components": list,
                        "rationale": list,
                    },
                    "timeline_and_logistics": list,
                    "technical_requirements": list,
                    "backup_entertainment_plans": {
                        "type": list,
                        "items": {
                            "scenario": str,
                            "plan": str,
                        }
                    },
                    "dependencies_on_other_areas": list,
                    "top_recommendations_and_rationale": {
                        "recommendation_1": {
                            "choice": str,
                            "reason": str,
                        },
                        "recommendation_2": {
                            "choice": str,
                            "reason": str,
                        },
                    },
                },
            },
            "communication": {
                "communication_recommendations": {
                    "overview": str,
                    "channels": list,
                    "key_messages": list,
                    "timeline": list,
                    "budget_overview": {
                        "total": (int, float),
                        "breakdown": dict,
                    },
                },
            },
            "budgeting": {
                "budget_allocation_recommended": dict,  # {category: {recommended_spend: number, pct_of_total: number, notes: str}}
                "major_category_breakdowns": dict,  # {category: {recommended_spend: number, pct_of_total: number, key_assumptions: list}}
                "what_if_scenarios": {
                    "type": list,
                    "items": {
                        "name": str,
                        "delta": str,
                        "impact": str,
                        "recommendation": str,
                    }
                },
                "scenario_recommendation": {
                    "name": str,
                    "reason": str,
                },
                "allocation_rationale": str,
                "warnings": list,
            },
            "scheduling": {
                "status": str,  # "optimal" | "feasible" | "infeasible"
                "optimized_schedule": {
                    "type": list,
                    "items": {
                        "session_id": (int, float),
                        "name": str,
                        "start_time": str,
                        "end_time": str,
                        "duration": (int, float),
                        "room": str,
                        "capacity": (int, float),
                        "speaker": str,
                        "expected_attendees": (int, float),
                        "date": str,
                    }
                },
                "metrics": {
                    "total_duration": (int, float, str),
                    "event_ends_at": str,
                    "room_utilization": dict,
                    "conflicts_resolved": str,
                },
                "conflicts_explained": list,
                "actionable_suggestions": list,
                "next_steps": list,
            },
        },
        "risks": {
            "type": list,
            "items": {
                "risk": str,
                "severity": str,  # "high" | "medium" | "low"
                "mitigation": str,
            }
        },
        "action_items": {
            "type": list,
            "items": {
                "action": str,
                "owner": str,
                "deadline": str,
                "priority": str,  # "high" | "medium" | "low"
            }
        },
        "assumptions": list,
    },
}


def schema_to_json_example(agent_name: str) -> str:
    """Convert a schema to a JSON structure example for agent instructions.
    
    Args:
        agent_name: The agent identifier (e.g., 'venue', 'budgeting')
    
    Returns:
        Formatted JSON structure string with examples suitable for LLM instructions
    """
    schema = AGENT_SCHEMAS.get(agent_name)
    if not schema:
        return "{}"
    
    def schema_type_to_example(field_name: str, schema_type: SchemaType, indent: int = 2) -> str:
        """Recursively convert a schema type to a JSON example."""
        spaces = " " * indent
        
        # Handle tuple (union types)
        if isinstance(schema_type, tuple):
            # Check if it includes numbers
            has_number = any(t in (int, float) for t in schema_type)
            has_string = str in schema_type
            
            if has_number and has_string:
                return '"string or number"  // Can be either'
            elif has_number:
                return '0  // Number'
            else:
                return '"string"'
        
        # Handle dict (nested schema)
        if isinstance(schema_type, dict):
            # Check if it's a list schema definition: {"type": list, "items": {...}}
            if "type" in schema_type and schema_type["type"] == list:
                if "items" in schema_type:
                    item_example = schema_type_to_example(f"{field_name}[]", schema_type["items"], indent + 2)
                    # Format as single-line array for readability
                    return f'[{item_example}]'
                else:
                    return '[]'
            
            # Otherwise it's a nested object schema
            lines = []
            for key, value_type in schema_type.items():
                example = schema_type_to_example(key, value_type, indent + 2)
                lines.append(f'{spaces}"{key}": {example},')
            
            if lines:
                return "{\n" + "\n".join(lines) + "\n" + " " * (indent - 2) + "}"
            else:
                return "{}"
        
        # Handle simple types
        if schema_type == str:
            if field_name == "status":
                return '"optimal"  // or "feasible" or "infeasible"'
            elif field_name in ["priority", "severity"]:
                return '"high"  // or "medium" or "low"'
            elif "url" in field_name.lower() or "website" in field_name.lower():
                return '"https://example.com"  // Must be valid URL with http:// or https://'
            elif "path" in field_name.lower():
                return '"path/to/file"'
            elif "date" in field_name.lower() or "deadline" in field_name.lower():
                return '"YYYY-MM-DD"'
            elif "time" in field_name.lower():
                return '"HH:MM"'
            else:
                return '"string"'
        elif schema_type == list:
            return '["string"]'
        elif schema_type == dict:
            return '{}'
        elif schema_type == int or schema_type == float:
            return '0  // Number'
        elif schema_type == bool:
            return 'true  // or false'
        else:
            return '"value"'
    
    def build_json_structure(schema_dict: Dict[str, Any], indent: int = 2) -> str:
        """Recursively build JSON structure from schema."""
        lines = []
        spaces = " " * indent
        
        for key, value in schema_dict.items():
            example_value = schema_type_to_example(key, value, indent)
            
            # Format the line
            lines.append(f'{spaces}"{key}": {example_value},')
        
        result = "{\n" + "\n".join(lines)
        # Remove trailing comma from last line
        result = result.rstrip(',')
        result += "\n" + " " * (indent - 2) + "}"
        return result
    
    return build_json_structure(schema)


def _validate_type(value: Any, expected_type: SchemaType, field_name: str) -> bool:
    """Validate that a value matches the expected type.
    
    Handles:
    - Simple types: str, list, dict, int, float, bool
    - Union types: (int, float), (str, int, float)
    - Nested schemas: dict with field definitions
    - List schemas: {"type": list, "items": {...}}
    """
    # Handle tuple (union types)
    if isinstance(expected_type, tuple):
        return any(_validate_type(value, t, field_name) for t in expected_type)
    
    # Handle dict (nested schema or list schema definition)
    if isinstance(expected_type, dict):
        # If it's a schema definition like {"type": list, "items": {...}}
        if "type" in expected_type:
            schema_type = expected_type["type"]
            if schema_type == list:
                # Value must be a list
                if not isinstance(value, list):
                    return False
                # Validate list items if schema provided
                if "items" in expected_type and isinstance(value, list):
                    item_schema = expected_type["items"]
                    for i, item in enumerate(value):
                        if not _validate_nested_schema(item, item_schema, f"{field_name}[{i}]"):
                            return False
                return True
            else:
                # For other types, validate against the type
                return _validate_type(value, schema_type, field_name)
        # Otherwise it's a nested object schema - validate recursively
        if not isinstance(value, dict):
            return False
        return _validate_nested_schema(value, expected_type, field_name)
    
    # Handle simple types
    if expected_type == str:
        return isinstance(value, str)
    elif expected_type == list:
        return isinstance(value, list)
    elif expected_type == dict:
        return isinstance(value, dict)
    elif expected_type == int or expected_type == float:
        return isinstance(value, (int, float))
    elif expected_type == bool:
        return isinstance(value, bool)
    else:
        return True


def _validate_nested_schema(value: Any, schema: Dict[str, Any], field_path: str = "") -> bool:
    """Recursively validate a value against a nested schema.
    
    Args:
        value: The value to validate
        schema: Schema definition (dict with field: type mappings)
        field_path: Path for error messages (e.g., "venues[0]")
    
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(value, dict):
        return False
    
    # Check all required fields in schema exist in value
    for key, expected_type in schema.items():
        if key not in value:
            # All fields in schema are required (we can add optional marking later if needed)
            return False
        
        field_value = value[key]
        
        # Validate type recursively
        if not _validate_type(field_value, expected_type, f"{field_path}.{key}" if field_path else key):
            return False
    
    return True


def _validate_nested_structure(value: Any, schema_def: Any, field_name: str) -> List[str]:
    """Validate nested structures based on schema definition.
    
    Returns list of validation errors (empty if valid).
    """
    errors = []
    
    # If schema_def is a dict (nested schema), validate recursively
    if isinstance(schema_def, dict):
        if "type" in schema_def:
            # It's a list with item schema
            if schema_def["type"] == list:
                if not isinstance(value, list):
                    errors.append(f"{field_name} must be a list")
                elif "items" in schema_def:
                    # Validate each item
                    item_schema = schema_def["items"]
                    for i, item in enumerate(value):
                        if not _validate_nested_schema(item, item_schema, f"{field_name}[{i}]"):
                            errors.append(f"{field_name}[{i}] does not match schema")
        else:
            # It's a nested object schema
            if not isinstance(value, dict):
                errors.append(f"{field_name} must be a dict")
            elif not _validate_nested_schema(value, schema_def, field_name):
                errors.append(f"{field_name} does not match nested schema")
    
    # Handle enum validation for specific fields
    if field_name == "status" and isinstance(value, str):
        valid_statuses = ["optimal", "feasible", "infeasible", "basic"]
        if value not in valid_statuses:
            errors.append(f"{field_name} must be one of: {', '.join(valid_statuses)}")
    elif field_name == "priority" and isinstance(value, str):
        valid_priorities = ["high", "medium", "low"]
        if value not in valid_priorities:
            errors.append(f"{field_name} must be one of: {', '.join(valid_priorities)}")
    elif field_name == "severity" and isinstance(value, str):
        valid_severities = ["high", "medium", "low"]
        if value not in valid_severities:
            errors.append(f"{field_name} must be one of: {', '.join(valid_severities)}")
    
    return errors


def validate_agent_output(agent_name: str, output: Any, required_agents: List[str] = None) -> Dict[str, Any]:
    """Validate and normalize agent output to match canonical schema.
    
    Enhanced validation that checks:
    - Top-level keys exist
    - Types match (str, list, dict, number)
    - Basic nested structure validation
    - Enum values are valid
    - For final_plan: ensures recommendations include data for all required_agents
    
    Args:
        agent_name: The agent identifier (e.g., 'venue', 'budgeting', 'final_plan')
        output: Raw output from the agent (string or dict)
        required_agents: List of agent names that were used (for final_plan validation)
    
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
    
    # Validate top-level keys exist
    missing_keys = [key for key in schema.keys() if key not in output]
    if missing_keys:
        raise ValueError(f"Agent '{agent_name}' missing required keys: {', '.join(missing_keys)}")
    
    # Validate types and nested structures recursively
    validation_errors = []
    for key, expected_type in schema.items():
        if key not in output:
            continue  # Already checked above
        
        value = output[key]
        
        # Special handling for recommendations: lenient validation (only validate what's present)
        if key == "recommendations" and agent_name == "final_plan":
            # For recommendations, only validate structure of what's present, not require all fields
            if not isinstance(value, dict):
                validation_errors.append(f"{key} must be a dict, got {type(value).__name__}")
            else:
                # Validate each present specialist output against its schema
                recommendations_schema = expected_type
                for agent_key, agent_data in value.items():
                    if agent_key in recommendations_schema:
                        agent_schema = recommendations_schema[agent_key]
                        if not _validate_type(agent_data, agent_schema, f"{key}.{agent_key}"):
                            validation_errors.append(f"{key}.{agent_key} does not match schema")
        else:
            # Normal validation for other fields
            if not _validate_type(value, expected_type, key):
                type_str = str(expected_type) if isinstance(expected_type, (tuple, dict)) else expected_type.__name__
                validation_errors.append(f"{key} must be {type_str}, got {type(value).__name__}")
            
            # Additional nested structure validation
            nested_errors = _validate_nested_structure(value, expected_type, key)
            validation_errors.extend(nested_errors)
    
    if validation_errors:
        raise ValueError(f"Agent '{agent_name}' validation errors: {'; '.join(validation_errors)}")
    
    # Special validation for final_plan: ensure recommendations include all required agents
    if agent_name == "final_plan" and required_agents:
        if "recommendations" not in output:
            raise ValueError(f"Agent '{agent_name}' missing 'recommendations' field")
        
        recommendations = output["recommendations"]
        if not isinstance(recommendations, dict):
            raise ValueError(f"Agent '{agent_name}' recommendations must be a dict, got {type(recommendations)}")
        
        # Filter out non-specialist agents (calendar, form, logo, planning)
        specialist_agents = [a for a in required_agents if a not in ["calendar", "form", "logo", "planning"]]
        
        missing_agents = []
        for agent in specialist_agents:
            if agent not in recommendations:
                missing_agents.append(agent)
            else:
                # Validate that the agent data structure matches its schema
                agent_data = recommendations[agent]
                if not isinstance(agent_data, dict):
                    missing_agents.append(f"{agent} (invalid structure)")
                else:
                    # Quick check: ensure it has at least one key (not empty)
                    if not agent_data:
                        missing_agents.append(f"{agent} (empty)")
        
        if missing_agents:
            raise ValueError(
                f"Agent '{agent_name}' recommendations missing required specialist data: {', '.join(missing_agents)}. "
                f"The coordinator must include COMPLETE output from all used agents in recommendations."
            )
    
    return output

