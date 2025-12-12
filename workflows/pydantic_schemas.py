"""Pydantic schemas for structured outputs following OpenAI Agents SDK best practices.

These schemas enforce JSON structure at the API level, ensuring agents return valid, 
parseable outputs that match our expected format. This eliminates JSON parsing errors
and makes the frontend integration more reliable.

Usage:
    from workflows.pydantic_schemas import VenueOutput, BudgetingOutput
    
    agent = Agent(
        name="Venue Specialist",
        instructions="...",
         output_type=VenueOutput
    )
"""
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import List, Dict, Any, Optional, Union, Literal


# ============================================================
# Planning Schema
# ============================================================
class PlanningOutput(BaseModel):
    """Output from the planning/coordination phase."""
    model_config = ConfigDict(extra="allow")
    analysis: str = Field(..., description="Analysis of event requirements")
    required_agents: List[str] = Field(..., description="List of required specialist agents")
    execution_order_rationale: str = Field(..., description="Explanation of agent execution order")
    special_considerations: List[str] = Field(..., description="Special considerations or constraints")


# ============================================================
# Venue Schema
# ============================================================
class VenueOption(BaseModel):
    """Individual venue option."""
    model_config = ConfigDict(extra="allow")
    name: str = Field(..., description="Venue name")
    location: str = Field(..., description="Venue location")
    capacity: Union[int, float] = Field(..., description="Maximum capacity")
    estimated_cost: Union[str, int, float] = Field(..., description="Estimated cost or cost range")
    amenities: List[str] = Field(..., description="List of amenities")
    availability_notes: str = Field(..., description="Notes on availability")
    website: str = Field(default="", description="Venue website URL (must be valid URL or empty string)")
    backup_alternatives: List[str] = Field(default_factory=list, description="Backup venue options")


class VenueTopRecommendation(BaseModel):
    """Top venue recommendation."""
    model_config = ConfigDict(extra="allow")
    option: str = Field(..., description="Name of recommended venue")
    rationale: str = Field(..., description="Reason for recommendation")
    dependencies: List[str] = Field(..., description="Dependencies or requirements")


class VenueOutput(BaseModel):
    """Complete venue recommendations output."""
    model_config = ConfigDict(extra="allow")
    summary: str = Field(..., description="Executive summary of venue recommendations")
    venues: List[VenueOption] = Field(..., description="List of venue options")
    timeline_and_logistics: List[str] = Field(..., description="Timeline and logistics steps")
    top_recommendation: VenueTopRecommendation = Field(..., description="Primary recommendation")


# ============================================================
# Catering Schema
# ============================================================
class CateringBudgetEstimate(BaseModel):
    """Budget estimate for catering."""
    model_config = ConfigDict(extra="allow")
    per_person: Union[int, float] = Field(..., description="Cost per person")
    total: Union[int, float] = Field(..., description="Total estimated cost")
    notes: str = Field(..., description="Budget notes and assumptions")


class CateringOutput(BaseModel):
    """Complete catering recommendations output."""
    model_config = ConfigDict(extra="allow")
    summary: str = Field(..., description="Executive summary of catering plan")
    menu_overview: List[str] = Field(..., description="Overview of menu options")
    dietary_accommodations: List[str] = Field(..., description="Dietary accommodations provided")
    budget_estimate: CateringBudgetEstimate = Field(..., description="Budget breakdown")
    timeline_and_logistics: List[str] = Field(..., description="Timeline and logistics steps")


# ============================================================
# Budgeting Schema
# ============================================================
class BudgetAllocationRecommended(BaseModel):
    """Recommended budget allocation."""
    model_config = ConfigDict(extra="allow")
    venue: Union[int, float] = Field(default=0, description="Venue budget")
    catering: Union[int, float] = Field(default=0, description="Catering budget")
    programme: Union[int, float] = Field(default=0, description="Programme budget")
    speakers: Union[int, float] = Field(default=0, description="Speakers budget")
    activities: Union[int, float] = Field(default=0, description="Activities budget")
    entertainment: Union[int, float] = Field(default=0, description="Entertainment budget")
    communication: Union[int, float] = Field(default=0, description="Communication budget")
    contingency: Union[int, float] = Field(default=0, description="Contingency fund")
    total_allocated: Union[int, float] = Field(..., description="Total allocated amount")
    total_budget: Union[int, float] = Field(..., description="Total available budget")
    status: Literal["within_budget", "over_budget", "at_limit"] = Field(..., description="Budget status")


class WhatIfScenario(BaseModel):
    """What-if scenario for budget planning."""
    model_config = ConfigDict(extra="allow")
    name: str = Field(..., description="Scenario name")
    delta: str = Field(..., description="Changes from baseline")
    impact: str = Field(..., description="Impact description")
    recommendation: str = Field(..., description="Recommendation for this scenario")


class ScenarioRecommendation(BaseModel):
    """Recommended scenario."""
    model_config = ConfigDict(extra="allow")
    name: str = Field(..., description="Recommended scenario name")
    reason: str = Field(..., description="Reason for recommendation")


class BudgetingOutput(BaseModel):
    """Complete budgeting analysis output."""
    model_config = ConfigDict(extra="allow")
    budget_allocation_recommended: BudgetAllocationRecommended = Field(..., description="Recommended allocation")
    major_category_breakdowns: Dict[str, Any] = Field(..., description="Detailed category breakdowns with nested sub-categories")
    what_if_scenarios: List[WhatIfScenario] = Field(..., description="Alternative scenarios")
    scenario_recommendation: ScenarioRecommendation = Field(..., description="Recommended scenario")
    allocation_rationale: str = Field(..., description="Rationale for allocation")
    warnings: List[str] = Field(default_factory=list, description="Budget warnings")


# ============================================================
# Programme Schema
# ============================================================
class ProgrammeOption(BaseModel):
    """Individual programme option."""
    model_config = ConfigDict(extra="allow")
    name: str = Field(..., description="Programme name")
    description: str = Field(..., description="Programme description")
    capacity: Union[str, int, float] = Field(..., description="Capacity")
    cost: Union[str, int, float] = Field(..., description="Estimated cost")
    amenities: List[str] = Field(..., description="Required amenities")
    dependencies: List[str] = Field(..., description="Dependencies")


class ProgrammeTopRecommendation(BaseModel):
    """Top programme recommendation."""
    model_config = ConfigDict(extra="allow")
    option: str = Field(..., description="Recommended option")
    rationale: str = Field(..., description="Rationale for recommendation")
    dependencies: Union[str, List[str]] = Field(..., description="Dependencies")


class ProgrammeBackupOption(BaseModel):
    """Backup programme option."""
    model_config = ConfigDict(extra="allow")
    option: str = Field(..., description="Backup option name")
    rationale: str = Field(..., description="Rationale for backup")


class ProgrammeRecommendations(BaseModel):
    """Programme recommendations structure."""
    model_config = ConfigDict(extra="allow")
    options: List[ProgrammeOption] = Field(..., description="Programme options")
    timeline_and_logistics: List[str] = Field(..., description="Timeline steps")
    session_and_flow: Dict[str, Any] = Field(..., description="Session flow details by day with time slots")
    breaks_networking: List[str] = Field(..., description="Break and networking details")
    technical_and_materials_requirements: List[str] = Field(..., description="Technical requirements")
    contingency_plans: List[str] = Field(..., description="Contingency plans")
    top_recommendation: ProgrammeTopRecommendation = Field(..., description="Top recommendation")
    backup_option: Optional[ProgrammeBackupOption] = Field(None, description="Backup option")


class ProgrammeOutput(BaseModel):
    """Complete programme planning output."""
    model_config = ConfigDict(extra="allow")
    summary: str = Field(..., description="Executive summary")
    programme_recommendations: ProgrammeRecommendations = Field(..., description="Detailed recommendations")
    next_steps: List[str] = Field(default_factory=list, description="Next steps")


# ============================================================
# Speakers Schema
# ============================================================
class SpeakerOption(BaseModel):
    """Individual speaker option."""
    model_config = ConfigDict(extra="allow")
    name: str = Field(..., description="Speaker name")
    bio: str = Field(..., description="Speaker bio")
    estimated_fee: Union[str, int, float] = Field(..., description="Estimated fee")
    ideal_role: str = Field(..., description="Ideal role at event")
    logistics: str = Field(..., description="Logistics notes")
    rationale: str = Field(..., description="Rationale for selection")
    company: str = Field(default="", description="Company or affiliation")
    image: str = Field(default="", description="Image URL")


class BackupPlan(BaseModel):
    """Backup plan for speakers."""
    model_config = ConfigDict(extra="allow")
    virtual_alternative: str = Field(..., description="Virtual alternative plan")
    local_rising_star: str = Field(..., description="Local backup speaker")


class SpeakersRecommendations(BaseModel):
    """Speakers recommendations structure."""
    model_config = ConfigDict(extra="allow")
    primary_objectives: List[str] = Field(..., description="Primary objectives")
    top_speaker_options: List[SpeakerOption] = Field(..., description="Top speaker options")
    honorarium_budget_itemization: Dict[str, Any] = Field(..., description="Budget breakdown")
    timeline_logistics: List[str] = Field(..., description="Timeline and logistics")
    technical_dependencies: List[str] = Field(..., description="Technical dependencies")
    other_dependencies: List[str] = Field(..., description="Other dependencies")
    backup_plan: BackupPlan = Field(..., description="Backup plan")


class SpeakersOutput(BaseModel):
    """Complete speakers recommendations output."""
    model_config = ConfigDict(extra="allow")
    summary: str = Field(..., description="Executive summary")
    speakers_recommendations: SpeakersRecommendations = Field(..., description="Detailed recommendations")
    recommendation_rationale: str = Field(..., description="Overall rationale")


# ============================================================
# Activities Schema
# ============================================================
class ActivityRecommendation(BaseModel):
    """Individual activity recommendation."""
    model_config = ConfigDict(extra="allow")
    name: str = Field(..., description="Activity name")
    description: str = Field(..., description="Activity description")
    duration: Union[str, int, float] = Field(..., description="Duration")
    cost_estimate: Union[str, int, float] = Field(..., description="Cost estimate")
    notes: str = Field(..., description="Additional notes")


class ActivityBudgetEstimate(BaseModel):
    """Budget estimate for activities."""
    model_config = ConfigDict(extra="allow")
    total: Union[int, float] = Field(..., description="Total cost")
    breakdown: Dict[str, Any] = Field(..., description="Cost breakdown by item")


class ActivityPlanning(BaseModel):
    """Activity planning structure."""
    model_config = ConfigDict(extra="allow")
    summary: str = Field(..., description="Executive summary")
    recommendations: List[ActivityRecommendation] = Field(..., description="Activity recommendations")
    logistics: List[str] = Field(..., description="Logistics details")
    budget_estimate: ActivityBudgetEstimate = Field(..., description="Budget estimate")
    timeline: List[str] = Field(default_factory=list, description="Activity timeline milestones")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies on other specialists")
    safety_planning: List[str] = Field(default_factory=list, description="Safety considerations")
    backup_activities: List[ActivityRecommendation] = Field(default_factory=list, description="Backup activity options")
    activity_metrics: List[str] = Field(default_factory=list, description="Success metrics for activities")


class ActivitiesOutput(BaseModel):
    """Complete activities planning output."""
    model_config = ConfigDict(extra="allow")
    activity_planning: ActivityPlanning = Field(..., description="Activity planning details")


# ============================================================
# Entertainment Schema
# ============================================================
class EntertainmentOption(BaseModel):
    """Individual entertainment option."""
    model_config = ConfigDict(extra="allow")
    name: str = Field(..., description="Entertainment name")
    description: str = Field(..., description="Description")
    cost_estimate: Union[int, float] = Field(..., description="Cost estimate")
    vendor_notes: str = Field(..., description="Vendor notes")


class EntertainmentBudgetEstimate(BaseModel):
    """Budget estimate for entertainment."""
    model_config = ConfigDict(extra="allow")
    total: Union[int, float] = Field(..., description="Total cost")
    breakdown: Dict[str, Any] = Field(..., description="Cost breakdown")


class RecommendedPackage(BaseModel):
    """Recommended entertainment package."""
    model_config = ConfigDict(extra="allow")
    option: str = Field(..., description="Package name")
    components: List[str] = Field(..., description="Package components")
    rationale: List[str] = Field(..., description="Rationale for package")


class BackupEntertainmentPlan(BaseModel):
    """Backup entertainment plan."""
    model_config = ConfigDict(extra="allow")
    scenario: str = Field(..., description="Scenario description")
    plan: str = Field(..., description="Backup plan")


class TopEntertainmentRecommendation(BaseModel):
    """Top recommendation details."""
    model_config = ConfigDict(extra="allow")
    choice: str = Field(..., description="Recommended choice")
    reason: str = Field(..., description="Reason for recommendation")


class TopRecommendationsAndRationale(BaseModel):
    """Top recommendations structure."""
    model_config = ConfigDict(extra="allow")
    recommendation_1: TopEntertainmentRecommendation = Field(..., description="First recommendation")
    recommendation_2: TopEntertainmentRecommendation = Field(..., description="Second recommendation")


class EntertainmentRecommendations(BaseModel):
    """Entertainment recommendations structure."""
    model_config = ConfigDict(extra="allow")
    summary: str = Field(..., description="Executive summary")
    specific_options: List[EntertainmentOption] = Field(..., description="Specific options")
    budget_estimate: EntertainmentBudgetEstimate = Field(..., description="Budget estimate")
    recommended_package: RecommendedPackage = Field(..., description="Recommended package")
    timeline_and_logistics: List[str] = Field(..., description="Timeline and logistics")
    technical_requirements: List[str] = Field(..., description="Technical requirements")
    backup_entertainment_plans: List[BackupEntertainmentPlan] = Field(..., description="Backup plans")
    dependencies_on_other_areas: List[str] = Field(..., description="Dependencies")
    top_recommendations_and_rationale: TopRecommendationsAndRationale = Field(..., description="Top recommendations")


class EntertainmentOutput(BaseModel):
    """Complete entertainment recommendations output."""
    model_config = ConfigDict(extra="allow")
    entertainment_recommendations: EntertainmentRecommendations = Field(..., description="Recommendations")


# ============================================================
# Communication Schema
# ============================================================
class CommunicationBudgetOverview(BaseModel):
    """Budget overview for communication."""
    model_config = ConfigDict(extra="allow")
    total: Union[int, float] = Field(..., description="Total budget")
    breakdown: Dict[str, Any] = Field(..., description="Budget breakdown")


class CommunicationRecommendations(BaseModel):
    """Communication recommendations structure."""
    model_config = ConfigDict(extra="allow")
    overview: str = Field(..., description="Overview")
    channels: List[str] = Field(..., description="Communication channels")
    key_messages: List[str] = Field(..., description="Key messages")
    timeline: List[str] = Field(..., description="Timeline")
    budget_overview: CommunicationBudgetOverview = Field(..., description="Budget overview")


class CommunicationOutput(BaseModel):
    """Complete communication plan output."""
    model_config = ConfigDict(extra="allow")
    communication_recommendations: CommunicationRecommendations = Field(..., description="Recommendations")


# ============================================================
# Scheduling Schema
# ============================================================
class ScheduledSession(BaseModel):
    """Individual scheduled session."""
    model_config = ConfigDict(extra="allow")
    session_id: Union[int, float] = Field(..., description="Session ID")
    name: str = Field(..., description="Session name")
    start_time: str = Field(..., description="Start time (HH:MM)")
    end_time: str = Field(..., description="End time (HH:MM)")
    duration: Union[int, float] = Field(..., description="Duration in minutes")
    room: str = Field(..., description="Room name")
    capacity: Union[int, float] = Field(..., description="Room capacity")
    speaker: str = Field(..., description="Speaker name")
    expected_attendees: Union[int, float] = Field(..., description="Expected attendees")
    date: Optional[str] = Field(None, description="Date (YYYY-MM-DD) for multi-day events")


class SchedulingMetrics(BaseModel):
    """Scheduling optimization metrics."""
    model_config = ConfigDict(extra="allow")
    total_duration: Union[int, float, str] = Field(..., description="Total event duration")
    event_ends_at: str = Field(..., description="Event end time")
    room_utilization: Dict[str, Any] = Field(..., description="Room utilization percentages")
    conflicts_resolved: str = Field(..., description="Number of conflicts resolved")


class SchedulingOutput(BaseModel):
    """Complete scheduling optimization output."""
    model_config = ConfigDict(extra="allow")
    status: Literal["optimal", "feasible", "infeasible"] = Field(..., description="Scheduling status")
    optimized_schedule: List[ScheduledSession] = Field(..., description="Optimized schedule")
    metrics: SchedulingMetrics = Field(..., description="Optimization metrics")
    conflicts_explained: List[str] = Field(default_factory=list, description="Explanation of conflicts")
    actionable_suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    next_steps: List[str] = Field(default_factory=list, description="Next steps")


# ============================================================
# Calendar Schema
# ============================================================
class CalendarOutput(BaseModel):
    """Calendar file output."""
    model_config = ConfigDict(extra="allow")
    calendar_file_path: str = Field(..., description="Path to calendar file")
    event_summary: str = Field(..., description="Event summary")
    timing_details: str = Field(..., description="Timing details")
    import_instructions: str = Field(..., description="Import instructions")


# ============================================================
# Form Schema
# ============================================================
class FormOutput(BaseModel):
    """Registration form output."""
    model_config = ConfigDict(extra="allow")
    form_url: str = Field(..., description="Form URL (must be valid URL or empty string)")
    status: Literal["success", "error"] = Field(..., description="Form creation status")
    message: str = Field(..., description="Status message")


# ============================================================
# Logo Schema
# ============================================================
class LogoOutput(BaseModel):
    """Logo generation output."""
    model_config = ConfigDict(extra="allow")
    status: Literal["optimal", "success", "error"] = Field(..., description="Logo generation status")
    logo_file_path: str = Field(..., description="Path to logo file")
    logo_url: str = Field(..., description="URL to logo file")
    design_rationale: str = Field(..., description="Design rationale")
    format_notes: str = Field(default="", description="Format and usage notes")


# ============================================================
# Final Plan Schema
# ============================================================
class TimelinePhase(BaseModel):
    """Timeline phase."""
    model_config = ConfigDict(extra="allow")
    phase: str = Field(..., description="Phase name")
    tasks: List[str] = Field(..., description="Tasks in this phase")
    deadline: str = Field(..., description="Deadline (YYYY-MM-DD)")


class ScheduleSession(BaseModel):
    """Schedule session for final plan."""
    model_config = ConfigDict(extra="allow")
    name: str = Field(..., description="Session name")
    start_time: str = Field(..., description="Start time")
    end_time: str = Field(..., description="End time")
    duration: Union[int, float, str] = Field(..., description="Duration")
    room: str = Field(..., description="Room")
    speaker: Optional[str] = Field(None, description="Speaker")
    date: Optional[str] = Field(None, description="Date (YYYY-MM-DD) for multi-day events")


class ScheduleMetrics(BaseModel):
    """Schedule metrics."""
    model_config = ConfigDict(extra="allow")
    total_duration: str = Field(..., description="Total duration")
    room_utilization: Dict[str, Any] = Field(default_factory=dict, description="Room utilization")
    conflicts_resolved: str = Field(default="0", description="Conflicts resolved")


class Schedule(BaseModel):
    """Schedule structure."""
    model_config = ConfigDict(extra="allow")
    optimized: bool = Field(..., description="Whether schedule is optimized")
    sessions: List[ScheduleSession] = Field(..., description="Sessions")
    metrics: Optional[ScheduleMetrics] = Field(None, description="Metrics (if optimized)")
    status: Literal["optimal", "feasible", "infeasible", "basic"] = Field(..., description="Schedule status")


class Budget(BaseModel):
    """Budget structure."""
    model_config = ConfigDict(extra="allow")
    total_available: Union[str, int, float] = Field(..., description="Total available budget")
    total_allocated: Union[str, int, float] = Field(..., description="Total allocated budget")
    by_category: Dict[str, Any] = Field(..., description="Budget by category")
    status: Literal["within_budget", "over_budget", "at_limit"] = Field(..., description="Budget status")


class Risk(BaseModel):
    """Risk item."""
    model_config = ConfigDict(extra="allow")
    risk: str = Field(..., description="Risk description")
    severity: Literal["high", "medium", "low"] = Field(..., description="Risk severity")
    mitigation: str = Field(..., description="Mitigation strategy")


class ActionItem(BaseModel):
    """Action item."""
    model_config = ConfigDict(extra="allow")
    action: str = Field(..., description="Action description")
    owner: str = Field(..., description="Owner/responsible party")
    deadline: str = Field(..., description="Deadline (YYYY-MM-DD)")
    priority: Literal["high", "medium", "low"] = Field(..., description="Priority level")


class FinalPlanOutput(BaseModel):
    """Complete final event plan output."""
    model_config = ConfigDict(extra="allow")
    executive_summary: str = Field(..., description="Executive summary (2-3 paragraphs)")
    timeline: List[TimelinePhase] = Field(..., description="Timeline phases")
    schedule: Schedule = Field(..., description="Event schedule")
    budget: Budget = Field(..., description="Budget breakdown")
    recommendations: Dict[str, Any] = Field(..., description="Complete specialist outputs")
    risks: List[Risk] = Field(..., description="Identified risks")
    action_items: List[ActionItem] = Field(..., description="Action items")
    assumptions: List[str] = Field(..., description="Key assumptions")


# ============================================================
# Schema Registry
# ============================================================
PYDANTIC_SCHEMAS = {
    "planning": PlanningOutput,
    "venue": VenueOutput,
    "catering": CateringOutput,
    "budgeting": BudgetingOutput,
    "programme": ProgrammeOutput,
    "speakers": SpeakersOutput,
    "activities": ActivitiesOutput,
    "entertainment": EntertainmentOutput,
    "communication": CommunicationOutput,
    "scheduling": SchedulingOutput,
    "calendar": CalendarOutput,
    "form": FormOutput,
    "logo": LogoOutput,
    "final_plan": FinalPlanOutput,
}


def get_pydantic_schema(agent_name: str) -> Optional[type[BaseModel]]:
    """Get Pydantic schema for an agent.
    
    Args:
        agent_name: Agent name (e.g., 'venue', 'budgeting')
        
    Returns:
        Pydantic BaseModel class or None if not found
    """
    return PYDANTIC_SCHEMAS.get(agent_name)
