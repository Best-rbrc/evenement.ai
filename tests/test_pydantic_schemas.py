"""Test suite for Pydantic schema validation.

Run with: pytest tests/test_pydantic_schemas.py -v
"""
import pytest
from pydantic import ValidationError
from workflows.pydantic_schemas import (
    VenueOutput,
    CateringOutput,
    BudgetingOutput,
    ProgrammeOutput,
    SpeakersOutput,
    ActivitiesOutput,
    EntertainmentOutput,
    CommunicationOutput,
    SchedulingOutput,
    CalendarOutput,
    FormOutput,
    LogoOutput,
    PlanningOutput,
    FinalPlanOutput,
)


def test_venue_output_valid():
    """Test VenueOutput with valid data."""
    data = {
        "summary": "Venue recommendations for the event",
        "venues": [
            {
                "name": "Convention Center",
                "location": "Downtown",
                "capacity": 500,
                "estimated_cost": "$25000",
                "amenities": ["AV equipment", "Catering"],
                "availability_notes": "Available on requested dates",
                "website": "https://example.com",
                "backup_alternatives": ["Alternative Venue 1"]
            }
        ],
        "timeline_and_logistics": ["Book venue by Jan 1", "Confirm setup by Feb 1"],
        "top_recommendation": {
            "option": "Convention Center",
            "rationale": "Best capacity and location",
            "dependencies": ["AV setup", "Catering confirmation"]
        }
    }
    venue = VenueOutput(**data)
    assert venue.summary == "Venue recommendations for the event"
    assert len(venue.venues) == 1
    assert venue.venues[0].capacity == 500


def test_venue_output_missing_required_field():
    """Test VenueOutput with missing required field."""
    data = {
        "summary": "Venue recommendations",
        "venues": [],
        "timeline_and_logistics": [],
        # Missing top_recommendation
    }
    with pytest.raises(ValidationError) as exc_info:
        VenueOutput(**data)
    assert "top_recommendation" in str(exc_info.value)


def test_budgeting_output_valid():
    """Test BudgetingOutput with valid data."""
    data = {
        "budget_allocation_recommended": {
            "venue": 50000,
            "catering": 30000,
            "total_allocated": 80000,
            "total_budget": 100000,
            "status": "within_budget"
        },
        "major_category_breakdowns": {
            "venue": {"rental": 40000, "setup": 10000}
        },
        "what_if_scenarios": [
            {
                "name": "Reduce catering",
                "delta": "-$10000",
                "impact": "Lower food quality",
                "recommendation": "Consider buffet style"
            }
        ],
        "scenario_recommendation": {
            "name": "Base scenario",
            "reason": "Best value for budget"
        },
        "allocation_rationale": "Balanced allocation across categories",
        "warnings": ["Contingency fund low"]
    }
    budget = BudgetingOutput(**data)
    assert budget.budget_allocation_recommended.status == "within_budget"
    assert budget.budget_allocation_recommended.total_allocated == 80000
    assert len(budget.what_if_scenarios) == 1


def test_budgeting_invalid_status():
    """Test BudgetingOutput with invalid status enum."""
    data = {
        "budget_allocation_recommended": {
            "total_allocated": 80000,
            "total_budget": 100000,
            "status": "invalid_status"  # Invalid enum value
        },
        "major_category_breakdowns": {},
        "what_if_scenarios": [],
        "scenario_recommendation": {"name": "test", "reason": "test"},
        "allocation_rationale": "test"
    }
    with pytest.raises(ValidationError) as exc_info:
        BudgetingOutput(**data)
    assert "status" in str(exc_info.value)


def test_planning_output_valid():
    """Test PlanningOutput with valid data."""
    data = {
        "analysis": "Event requires venue, catering, and speakers",
        "required_agents": ["venue", "catering", "speakers", "budgeting"],
        "execution_order_rationale": "Venue first to secure location, then catering",
        "special_considerations": ["Check dietary requirements", "AV equipment needed"]
    }
    planning = PlanningOutput(**data)
    assert len(planning.required_agents) == 4
    assert "venue" in planning.required_agents


def test_final_plan_output_valid():
    """Test FinalPlanOutput with valid data."""
    data = {
        "executive_summary": "Comprehensive event plan for conference",
        "timeline": [
            {
                "phase": "Pre-Event Planning",
                "tasks": ["Book venue", "Confirm speakers"],
                "deadline": "2026-01-15"
            }
        ],
        "schedule": {
            "optimized": True,
            "sessions": [
                {
                    "name": "Opening Keynote",
                    "start_time": "09:00",
                    "end_time": "10:00",
                    "duration": 60,
                    "room": "Main Hall",
                    "speaker": "John Doe",
                    "date": "2026-03-15"
                }
            ],
            "metrics": {
                "total_duration": "8 hours",
                "room_utilization": {"Main Hall": "85%"},
                "conflicts_resolved": "3"
            },
            "status": "optimal"
        },
        "budget": {
            "total_available": "$100000",
            "total_allocated": "$95000",
            "by_category": {"venue": 50000, "catering": 30000},
            "status": "within_budget"
        },
        "recommendations": {
            "venue": {"summary": "test"},
            "catering": {"summary": "test"}
        },
        "risks": [
            {
                "risk": "Venue cancellation",
                "severity": "high",
                "mitigation": "Book backup venue"
            }
        ],
        "action_items": [
            {
                "action": "Sign venue contract",
                "owner": "Event Manager",
                "deadline": "2026-01-10",
                "priority": "high"
            }
        ],
        "assumptions": ["Weather will be favorable", "All speakers confirm attendance"]
    }
    final_plan = FinalPlanOutput(**data)
    assert len(final_plan.timeline) == 1
    assert len(final_plan.schedule.sessions) == 1
    assert final_plan.schedule.status == "optimal"
    assert len(final_plan.risks) == 1
    assert final_plan.risks[0].severity == "high"


def test_form_output_valid():
    """Test FormOutput with valid data."""
    data = {
        "form_url": "https://tally.so/r/abc123",
        "status": "success",
        "message": "Form created successfully"
    }
    form = FormOutput(**data)
    assert form.form_url.startswith("https://")
    assert form.status == "success"


def test_calendar_output_valid():
    """Test CalendarOutput with valid data."""
    data = {
        "calendar_file_path": "event_outputs/event.ics",
        "event_summary": "Annual Conference 2026",
        "timing_details": "March 15-17, 2026",
        "import_instructions": "Import into calendar app"
    }
    calendar = CalendarOutput(**data)
    assert calendar.calendar_file_path.endswith(".ics")


def test_scheduling_output_valid():
    """Test SchedulingOutput with valid data."""
    data = {
        "status": "optimal",
        "optimized_schedule": [
            {
                "session_id": 1,
                "name": "Opening Session",
                "start_time": "09:00",
                "end_time": "10:00",
                "duration": 60,
                "room": "Room A",
                "capacity": 200,
                "speaker": "Jane Doe",
                "expected_attendees": 180
            }
        ],
        "metrics": {
            "total_duration": "8 hours",
            "event_ends_at": "17:00",
            "room_utilization": {"Room A": "90%"},
            "conflicts_resolved": "2"
        }
    }
    schedule = SchedulingOutput(**data)
    assert schedule.status == "optimal"
    assert len(schedule.optimized_schedule) == 1


def test_union_field_types():
    """Test that union fields accept multiple types."""
    # Test with string
    venue_data = {
        "summary": "test",
        "venues": [{
            "name": "Test Venue",
            "location": "City",
            "capacity": 100,
            "estimated_cost": "$25000",  # String
            "amenities": [],
            "availability_notes": "Available",
            "website": "https://example.com"
        }],
        "timeline_and_logistics": [],
        "top_recommendation": {
            "option": "Test Venue",
            "rationale": "Best option",
            "dependencies": []
        }
    }
    venue1 = VenueOutput(**venue_data)
    assert isinstance(venue1.venues[0].estimated_cost, str)
    
    # Test with number
    venue_data["venues"][0]["estimated_cost"] = 25000  # Number
    venue2 = VenueOutput(**venue_data)
    assert isinstance(venue2.venues[0].estimated_cost, int)


def test_model_dump():
    """Test that model_dump() returns dict correctly."""
    data = {
        "analysis": "Test analysis",
        "required_agents": ["venue", "catering"],
        "execution_order_rationale": "Logical order",
        "special_considerations": []
    }
    planning = PlanningOutput(**data)
    dumped = planning.model_dump()
    
    assert isinstance(dumped, dict)
    assert dumped["analysis"] == "Test analysis"
    assert len(dumped["required_agents"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
