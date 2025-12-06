"""FastAPI server exposing the event planning workflow for the frontend.

Run with:
    uvicorn server:app --reload --port 8000
"""
from __future__ import annotations

import asyncio
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from workflows.event_planning_workflow import run_event_planning

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()

app = FastAPI(title="AI Event Planner API", version="0.1.0")

# Allow local dev frontend by default; can be narrowed via env var
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory cache for the last successful result (dev testing only)
_last_result_cache: Optional[dict] = None


class EventRequest(BaseModel):
    """Payload sent by the frontend form.

    Uses camelCase to match the existing UI; additional aliases could be
    added later if the CLI payload is posted directly.
    """

    eventType: str = Field(..., description="Event type selected by the user")
    customEventType: Optional[str] = Field(None, description="Custom event type when 'Other' is chosen")
    eventName: str = Field(..., description="Name of the event")
    dateType: str = Field("single", description="'single' or 'range'")
    eventDate: str = Field(..., description="Start date or single date")
    endDate: Optional[str] = Field(None, description="End date when dateType is 'range'")
    startTime: Optional[str] = Field(None, description="Optional start time")
    endTime: Optional[str] = Field(None, description="Optional end time")
    locationPreference: str = Field(..., description="Preferred location or city")
    budgetMin: float = Field(..., description="Minimum budget in USD")
    budgetMax: float = Field(..., description="Maximum budget in USD")
    guestCountMin: int = Field(..., description="Minimum expected attendees")
    guestCountMax: int = Field(..., description="Maximum expected attendees")
    specialRequirements: str = Field("", description="Free-text requirements or themes")
    enableSandbox: Optional[bool] = Field(False, description="Enable sandboxed form creation")
    enableSMS: Optional[bool] = Field(False, description="Enable SMS notifications")

    model_config = {"populate_by_name": True, "extra": "allow"}


class PlanResponse(BaseModel):
    status: str
    event_details: dict
    result: dict


def _format_range(min_value: float | int, max_value: float | int, prefix: str = "") -> str:
    return f"{prefix}{min_value:,.0f}-{prefix}{max_value:,.0f}" if max_value else f"{prefix}{min_value:,.0f}"


def map_request_to_workflow_payload(payload: EventRequest) -> dict:
    """Convert the frontend payload into the workflow's expected shape."""
    event_type = payload.customEventType or payload.eventType
    if payload.eventType.lower() == "other" and payload.customEventType:
        event_type = payload.customEventType

    date_value = payload.eventDate
    if payload.dateType == "range" and payload.endDate:
        date_value = f"{payload.eventDate} to {payload.endDate}"

    time_window = None
    if payload.startTime or payload.endTime:
        start = payload.startTime or ""
        end = payload.endTime or ""
        time_window = f"{start} - {end}".strip()

    return {
        "event_type": event_type,
        "event_name": payload.eventName,
        "event_date": date_value,
        "location_preference": payload.locationPreference,
        "budget_range": _format_range(payload.budgetMin, payload.budgetMax, prefix="$"),
        "guest_count": _format_range(payload.guestCountMin, payload.guestCountMax),
        "special_requirements": payload.specialRequirements.strip(),
        "time_window": time_window,
    }


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/plan/last")
async def get_last_plan():
    """Return the last successful plan result from cache (dev testing only)."""
    global _last_result_cache
    if not _last_result_cache:
        raise HTTPException(status_code=404, detail="No cached result available. Run POST /api/plan first.")
    # Return raw dict instead of re-validating through Pydantic
    return _last_result_cache


@app.post("/api/plan", response_model=PlanResponse)
async def create_plan(payload: EventRequest) -> PlanResponse:
    global _last_result_cache
    
    # Map incoming payload to the existing workflow schema
    event_details = map_request_to_workflow_payload(payload)

    # Set non-interactive mode and dev settings for API calls
    os.environ["EVENT_PLANNER_NON_INTERACTIVE"] = "1"
    os.environ["EVENT_PLANNER_ENABLE_SANDBOX"] = "1" if payload.enableSandbox else "0"
    os.environ["EVENT_PLANNER_ENABLE_SMS"] = "1" if payload.enableSMS else "0"
    
    # Run the long-running workflow in a worker thread to avoid blocking the loop
    try:
        result = await asyncio.to_thread(run_event_planning, event_details)
    except Exception as exc:  # noqa: BLE001 - surface full error to client
        raise HTTPException(status_code=500, detail=str(exc))

    response = PlanResponse(status="ok", event_details=event_details, result=result)
    
    # Cache the successful result
    _last_result_cache = response.model_dump()
    
    return response


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
