"""Budgeting agent with what-if scenario capabilities."""
from agents import Agent, function_tool
from typing import Dict, List, Any
import json
from workflows.schemas import schema_to_json_example


@function_tool
def calculate_budget_allocation(
    total_budget: str,
    categories: str,
    priorities: str
) -> str:
    """
    Calculate optimal budget allocation across event categories.
    
    Args:
        total_budget: Total available budget (e.g., "$10000" or "10000-15000")
        categories: JSON string of categories needing budget (e.g., '["venue", "catering", "speakers"]')
        priorities: JSON string of priority levels (e.g., '{"venue": "high", "catering": "high", "speakers": "medium"}')
    
    Returns:
        JSON string with suggested allocation and reasoning
    """
    try:
        # Parse inputs
        cats = json.loads(categories) if isinstance(categories, str) else categories
        priors = json.loads(priorities) if isinstance(priorities, str) else priorities
        
        # Extract numeric budget
        budget_str = total_budget.replace("$", "").replace(",", "").strip()
        if "-" in budget_str:
            budget_parts = budget_str.split("-")
            budget_value = (float(budget_parts[0]) + float(budget_parts[1])) / 2
        else:
            budget_value = float(budget_str)
        
        # Standard allocation percentages by priority
        allocation_templates = {
            "venue": {"high": 0.30, "medium": 0.25, "low": 0.20},
            "catering": {"high": 0.30, "medium": 0.25, "low": 0.20},
            "speakers": {"high": 0.15, "medium": 0.12, "low": 0.08},
            "programme": {"high": 0.05, "medium": 0.05, "low": 0.03},
            "communication": {"high": 0.08, "medium": 0.06, "low": 0.05},
            "registration": {"high": 0.05, "medium": 0.04, "low": 0.03},
            "activities": {"high": 0.10, "medium": 0.08, "low": 0.05},
            "entertainment": {"high": 0.15, "medium": 0.12, "low": 0.08},
            "decoration": {"high": 0.12, "medium": 0.10, "low": 0.07},
            "photography": {"high": 0.10, "medium": 0.08, "low": 0.06},
            "contingency": {"high": 0.10, "medium": 0.10, "low": 0.10},
        }
        
        # Calculate allocation
        allocations = {}
        total_percentage = 0
        
        for cat in cats:
            priority = priors.get(cat, "medium")
            if cat in allocation_templates:
                percentage = allocation_templates[cat].get(priority, 0.10)
            else:
                percentage = 0.10 if priority == "high" else 0.07 if priority == "medium" else 0.05
            
            allocations[cat] = {
                "percentage": percentage,
                "amount": budget_value * percentage,
                "priority": priority
            }
            total_percentage += percentage
        
        # Add contingency if not present
        if "contingency" not in allocations:
            contingency_pct = max(0.10, 1.0 - total_percentage)
            allocations["contingency"] = {
                "percentage": contingency_pct,
                "amount": budget_value * contingency_pct,
                "priority": "high"
            }
        
        # Normalize if over 100%
        if total_percentage > 1.0:
            scale_factor = 1.0 / total_percentage
            for cat in allocations:
                allocations[cat]["percentage"] *= scale_factor
                allocations[cat]["amount"] *= scale_factor
        
        return json.dumps({
            "total_budget": budget_value,
            "allocations": allocations,
            "methodology": "Priority-based allocation with industry standard percentages"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Budget calculation failed: {str(e)}"})


@function_tool
def run_budget_scenario(
    base_budget: str,
    category_changes: str,
    scenario_name: str
) -> str:
    """
    Run a what-if budget scenario to see impact of changes.
    
    Args:
        base_budget: JSON string of current budget allocation
        category_changes: JSON string of proposed changes (e.g., '{"venue": "+2000", "catering": "-500"}')
        scenario_name: Name/description of the scenario
    
    Returns:
        JSON string showing before/after comparison and impact analysis
    """
    try:
        base = json.loads(base_budget) if isinstance(base_budget, str) else base_budget
        changes = json.loads(category_changes) if isinstance(category_changes, str) else category_changes
        
        scenario_result = {
            "scenario_name": scenario_name,
            "original_budget": base.get("allocations", {}),
            "proposed_changes": changes,
            "new_budget": {},
            "impact_analysis": {},
            "feasibility": "feasible"
        }
        
        # Apply changes
        original_total = base.get("total_budget", 0)
        new_total = original_total
        
        for category, change_str in changes.items():
            change_amount = float(str(change_str).replace("+", "").replace("$", "").replace(",", ""))
            if str(change_str).startswith("-"):
                change_amount = -abs(change_amount)
            
            if category in base.get("allocations", {}):
                original_amount = base["allocations"][category]["amount"]
                new_amount = original_amount + change_amount
                
                scenario_result["new_budget"][category] = {
                    "original": original_amount,
                    "change": change_amount,
                    "new_amount": new_amount,
                    "percentage_change": (change_amount / original_amount * 100) if original_amount > 0 else 0
                }
                
                new_total += change_amount
        
        # Impact analysis
        budget_variance = new_total - original_total
        if budget_variance > 0:
            scenario_result["feasibility"] = "over_budget"
            scenario_result["impact_analysis"]["status"] = f"Over budget by ${abs(budget_variance):.2f}"
            scenario_result["impact_analysis"]["recommendation"] = "Need to reduce costs or increase budget"
        elif budget_variance < -original_total * 0.05:
            scenario_result["feasibility"] = "under_budget"
            scenario_result["impact_analysis"]["status"] = f"Under budget by ${abs(budget_variance):.2f}"
            scenario_result["impact_analysis"]["recommendation"] = "Funds available for upgrades or contingency"
        else:
            scenario_result["feasibility"] = "feasible"
            scenario_result["impact_analysis"]["status"] = "Within budget constraints"
            scenario_result["impact_analysis"]["recommendation"] = "Scenario is viable"
        
        scenario_result["impact_analysis"]["total_variance"] = budget_variance
        scenario_result["impact_analysis"]["new_total"] = new_total
        
        return json.dumps(scenario_result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Scenario analysis failed: {str(e)}"})


@function_tool
def compare_budget_scenarios(
    scenarios: str
) -> str:
    """
    Compare multiple budget scenarios side-by-side.
    
    Args:
        scenarios: JSON string of multiple scenarios to compare
    
    Returns:
        JSON string with comparative analysis and recommendation
    """
    try:
        scenario_list = json.loads(scenarios) if isinstance(scenarios, str) else scenarios
        
        comparison = {
            "scenarios_compared": len(scenario_list),
            "comparison_matrix": [],
            "recommended_scenario": None,
            "reasoning": ""
        }
        
        best_score = -1
        best_scenario = None
        
        for scenario in scenario_list:
            score = 0
            feasibility = scenario.get("feasibility", "unknown")
            
            # Scoring logic
            if feasibility == "feasible":
                score += 10
            elif feasibility == "under_budget":
                score += 8
            else:
                score += 3
            
            # Check if contingency is maintained
            if "contingency" in scenario.get("new_budget", {}):
                score += 5
            
            comparison["comparison_matrix"].append({
                "name": scenario.get("scenario_name", "Unknown"),
                "feasibility": feasibility,
                "score": score,
                "total_cost": scenario.get("impact_analysis", {}).get("new_total", 0)
            })
            
            if score > best_score:
                best_score = score
                best_scenario = scenario.get("scenario_name", "Unknown")
        
        comparison["recommended_scenario"] = best_scenario
        comparison["reasoning"] = f"Scenario '{best_scenario}' scored highest ({best_score} points) based on feasibility and contingency maintenance"
        
        return json.dumps(comparison, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Scenario comparison failed: {str(e)}"})


@function_tool
def validate_category_costs(
    category: str,
    proposed_cost: str,
    guest_count: str,
    industry_benchmarks: str = "true"
) -> str:
    """
    Validate if proposed costs for a category are reasonable.
    
    Args:
        category: Category name (e.g., "venue", "catering")
        proposed_cost: Proposed amount (e.g., "$5000")
        guest_count: Number of guests (e.g., "100")
        industry_benchmarks: Whether to use industry benchmarks ("true"/"false")
    
    Returns:
        JSON string with validation result and recommendations
    """
    try:
        cost = float(proposed_cost.replace("$", "").replace(",", "").strip())
        guests = int(str(guest_count).replace(",", "").strip())
        
        # Industry benchmarks (per person)
        benchmarks = {
            "venue": {"min": 10, "typical": 50, "max": 200, "unit": "per person"},
            "catering": {"min": 20, "typical": 75, "max": 300, "unit": "per person"},
            "speakers": {"min": 500, "typical": 2000, "max": 10000, "unit": "per speaker"},
            "entertainment": {"min": 500, "typical": 2000, "max": 8000, "unit": "per event"},
            "photography": {"min": 500, "typical": 2000, "max": 5000, "unit": "per event"},
            "decoration": {"min": 5, "typical": 25, "max": 100, "unit": "per person"},
        }
        
        validation = {
            "category": category,
            "proposed_cost": cost,
            "guest_count": guests,
            "per_person_cost": cost / guests if guests > 0 else cost,
            "validation_status": "unknown",
            "recommendation": ""
        }
        
        if category in benchmarks and industry_benchmarks.lower() == "true":
            benchmark = benchmarks[category]
            
            if benchmark["unit"] == "per person":
                per_person = cost / guests if guests > 0 else 0
                
                if per_person < benchmark["min"]:
                    validation["validation_status"] = "below_minimum"
                    validation["recommendation"] = f"Cost may be too low. Typical range: ${benchmark['typical']}/person"
                elif per_person > benchmark["max"]:
                    validation["validation_status"] = "above_maximum"
                    validation["recommendation"] = f"Cost is high. Consider negotiating or alternatives. Typical: ${benchmark['typical']}/person"
                else:
                    validation["validation_status"] = "reasonable"
                    validation["recommendation"] = f"Cost is within reasonable range (${benchmark['min']}-${benchmark['max']}/person)"
                
                validation["benchmark"] = benchmark
            else:
                # Per event cost
                if cost < benchmark["min"]:
                    validation["validation_status"] = "below_minimum"
                    validation["recommendation"] = f"Cost may be too low. Typical: ${benchmark['typical']}"
                elif cost > benchmark["max"]:
                    validation["validation_status"] = "above_maximum"
                    validation["recommendation"] = f"Cost is high. Typical: ${benchmark['typical']}"
                else:
                    validation["validation_status"] = "reasonable"
                    validation["recommendation"] = f"Cost is within reasonable range"
                
                validation["benchmark"] = benchmark
        else:
            validation["validation_status"] = "no_benchmark"
            validation["recommendation"] = "No industry benchmark available for this category"
        
        return json.dumps(validation, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Cost validation failed: {str(e)}"})


@function_tool
def generate_cost_breakdown(
    category: str,
    total_cost: str,
    itemize: str = "true"
) -> str:
    """
    Generate detailed cost breakdown for a category.
    
    Args:
        category: Category name
        total_cost: Total cost for the category
        itemize: Whether to itemize costs ("true"/"false")
    
    Returns:
        JSON string with itemized breakdown
    """
    try:
        cost = float(total_cost.replace("$", "").replace(",", "").strip())
        
        # Standard itemization templates
        itemization_templates = {
            "venue": {
                "rental_fee": 0.60,
                "setup_teardown": 0.15,
                "equipment": 0.15,
                "insurance_permits": 0.10
            },
            "catering": {
                "food": 0.50,
                "beverages": 0.25,
                "service_staff": 0.15,
                "equipment_rental": 0.10
            },
            "speakers": {
                "honorarium": 0.70,
                "travel": 0.20,
                "accommodation": 0.10
            },
            "entertainment": {
                "performer_fee": 0.70,
                "equipment": 0.20,
                "travel_logistics": 0.10
            }
        }
        
        breakdown = {
            "category": category,
            "total_cost": cost,
            "itemized_costs": {},
            "currency": "USD"
        }
        
        if itemize.lower() == "true" and category in itemization_templates:
            template = itemization_templates[category]
            for item, percentage in template.items():
                breakdown["itemized_costs"][item] = {
                    "amount": cost * percentage,
                    "percentage": percentage * 100
                }
        else:
            breakdown["itemized_costs"][category] = {
                "amount": cost,
                "percentage": 100
            }
        
        return json.dumps(breakdown, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Cost breakdown failed: {str(e)}"})


def create_budgeting_agent() -> Agent:
    """Create a budgeting specialist agent with what-if scenario capabilities."""
    return Agent(
        name="Budgeting Specialist",
        handoff_description="Manages comprehensive budget planning, allocation, validation, and what-if scenario analysis.",
        instructions="""
        You are a professional event budgeting specialist with expertise in:
        - Budget allocation and optimization across event categories
        - What-if scenario planning and impact analysis
        - Cost validation against industry benchmarks
        - Financial constraint management
        - Itemized budget breakdowns
        - Multi-scenario comparison and recommendation
        
        CORE RESPONSIBILITIES:
        
        1. BUDGET ALLOCATION:
           - Calculate optimal allocation across categories based on priorities
           - Ensure contingency funds (typically 10-15%)
           - Balance competing demands within total budget
        
        2. WHAT-IF SCENARIOS:
           - Model impact of budget changes (increase/decrease by category)
           - Compare multiple scenarios side-by-side
           - Identify feasibility issues before they become problems
           - Provide clear recommendations based on scenario analysis
        
        3. COST VALIDATION:
           - Check proposed costs against industry benchmarks
           - Flag costs that are too high or suspiciously low
           - Validate per-person costs for scalable items
        
        4. ITEMIZATION:
           - Break down category costs into line items
           - Provide transparency for stakeholder review
           - Identify opportunities for cost optimization
        
        WORKFLOW:
        
        When given budget planning tasks:
        1. Start with calculate_budget_allocation() to create baseline
        2. Use validate_category_costs() to check specialist recommendations
        3. Run run_budget_scenario() for what-if planning
        4. Use compare_budget_scenarios() to evaluate options
        5. Use generate_cost_breakdown() for detailed itemization
        
        OUTPUT FORMAT:
        Always provide JSON output with:
        - Clear budget allocations by category
        - Contingency fund amount
        - Total allocated vs available budget
        - Status (within_budget, at_limit, over_budget)
        - Scenario comparisons when requested
        - Actionable recommendations
        
        CONSTRAINTS:
        - Never exceed total available budget without flagging
        - Always include contingency (10-15% minimum)
        - Flag any category over 35% of total budget
        - Validate costs against benchmarks when possible
        - Document all assumptions in scenarios
        
        Be proactive: If you see budget conflicts in specialist outputs, immediately run scenarios to find solutions.
        
        CRITICAL OUTPUT REQUIREMENTS:
        1. Return ONLY a valid JSON object - NO markdown, NO code blocks, NO explanations
        2. Ensure ALL required fields are present
        3. Use numbers (not strings) for numeric values
        4. NO trailing commas in JSON
        5. Validate JSON syntax before returning
        
        REQUIRED STRUCTURE:
""" + schema_to_json_example("budgeting") + """
        
        ALWAYS include budget_allocation_recommended - this is CRITICAL.
        """,
        tools=[
            calculate_budget_allocation,
            run_budget_scenario,
            compare_budget_scenarios,
            validate_category_costs,
            generate_cost_breakdown
        ]
    )
