"""FastAPI server exposing the event planning workflow for the frontend.

Run with:
    uvicorn server:app --reload --port 8000
"""
from __future__ import annotations

import asyncio
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
from openai import OpenAI

from workflows.event_planning_workflow import run_event_planning
from workflows.plan_refinement import refine_event_plan

# Setup server logging
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def setup_server_logger():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"server_{timestamp}.log"
    logger = logging.getLogger("server")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

server_logger = setup_server_logger()

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

# Progress tracking for real-time updates
_current_progress: dict = {
    "phase": "idle",
    "status": "waiting",
    "agents": [],
    "current_agent": None,
    "message": ""
}


class VoiceInput(BaseModel):
    """Payload for voice dictation input."""
    transcript: str = Field(..., description="The transcribed speech from the user")


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


class RefinePlanRequest(BaseModel):
    """Payload for plan refinement requests."""
    message: str = Field(..., description="User's chat message requesting changes")
    current_plan: dict = Field(..., description="Current final_plan JSON")
    specialist_outputs: dict = Field(..., description="Current specialist outputs")
    event_details: dict = Field(..., description="Original event details")
    required_agents: list = Field(..., description="List of agents that were originally used")


class RefinePlanResponse(BaseModel):
    """Response from plan refinement."""
    updated_plan: dict = Field(..., description="Updated final_plan")
    changed_sections: list = Field(..., description="List of sections that changed")
    agents_called: list = Field(..., description="List of agents that were called")
    coordinator_message: str = Field(..., description="Message from coordinator explaining changes")
    error: Optional[str] = Field(None, description="Error message if refinement failed")


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


@app.get("/api/plan/status")
async def plan_status() -> dict:
    """Get current planning progress status."""
    global _current_progress
    return _current_progress


@app.get("/api/plan/last")
async def get_last_plan():
    """Return the last successful plan result from cache (dev testing only)."""
    global _last_result_cache
    if not _last_result_cache:
        raise HTTPException(status_code=404, detail="No cached result available. Run POST /api/plan first.")
    # Return raw dict instead of re-validating through Pydantic
    return _last_result_cache


@app.get("/api/files/{file_path:path}")
async def get_file(file_path: str):
    """Serve files from event_outputs directory."""
    import os
    from pathlib import Path
    
    # Security: prevent directory traversal
    if '..' in file_path or file_path.startswith('/'):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Construct full path
    event_outputs_dir = Path(__file__).parent / "event_outputs"
    full_path = event_outputs_dir / file_path
    
    # Ensure file is within event_outputs directory
    try:
        full_path.resolve().relative_to(event_outputs_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(full_path),
        filename=full_path.name,
        media_type='application/octet-stream'
    )


@app.post("/api/voice-to-form")
async def voice_to_form(payload: VoiceInput) -> dict:
    """Parse voice transcript and extract event details using OpenAI."""
    # Basic request diagnostics
    transcript_len = len(payload.transcript or "")
    server_logger.info("=" * 80)
    server_logger.info(" /api/voice-to-form called")
    server_logger.info(f"Transcript length: {transcript_len}")
    server_logger.info(f"Full transcript: {payload.transcript}")
    print(f"\n /api/voice-to-form endpoint called")
    print(f"   Transcript length: {transcript_len}")
    print(f"   Transcript: {payload.transcript}")
    
    if not payload.transcript or not payload.transcript.strip():
        server_logger.warning(" Empty transcript received")
        print(" Empty transcript received")
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")
    
    try:
        system_prompt = """You are an AI assistant that extracts event planning details from natural speech transcripts.

Extract ONLY the information explicitly mentioned by the user. Do not infer or make up any details.
If a field is not mentioned, set it to null.

Return a JSON object with these fields:
- eventType: string (one of: "Tech Conference", "Workshop", "Hackathon", "Corporate Gala", "Wedding", "Academic Symposium", "Festival", "Other")
- customEventType: string or null (only if eventType is "Other")
- eventName: string or null (preserve exact capitalization - e.g., "START Hack" not "Star Tech")
- dateType: "single" or "range" (use "range" if multiple days mentioned, "single" for one day)
- eventDate: string in YYYY-MM-DD format or null
- endDate: string in YYYY-MM-DD format or null (only if multiple days mentioned)
- startTime: string in HH:MM 24-hour format or null
- endTime: string in HH:MM 24-hour format or null
- locationPreference: string or null (format as "City, Country" e.g., "St. Gallen, Switzerland" - use proper city names)
- budgetMin: number or null (in USD)
- budgetMax: number or null (in USD)
- guestCountMin: number or null
- guestCountMax: number or null
- specialRequirements: string or null (any other details mentioned)

IMPORTANT RULES:
1. For dates: If user says "March 23-26" or mentions multiple days, infer year as 2026 and set dateType to "range"
2. For budget: Extract numbers ("150 to 300 grand" = budgetMin: 150000, budgetMax: 300000)
3. For locations: Correct common speech recognition errors ("sent Allen" = "St. Gallen", "Allen" = "St. Gallen")
4. For event names: Preserve capitalization patterns ("Star Tech" likely means "START Hack" for hackathons)
5. For times: Convert to 24-hour format ("4 PM" = "16:00", "5 PM" = "17:00")
6. For guest count: Look for attendee numbers ("500 to 600 hackers" = guestCountMin: 500, guestCountMax: 600)
7. Common location corrections: "sent Allen" or "sent galen" or "Allen" in Switzerland context = "St. Gallen, Switzerland"
8. Common event name corrections for hackathons: "Star Tech" = "START Hack", "start hack" = "START Hack"""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract event details from: {payload.transcript}"}
            ],
             output_type={"type": "json_object"},
            temperature=0.1
        )
        
        # Log raw response metadata (not the whole content to avoid noise)
        server_logger.info("OpenAI response received")
        server_logger.info(f"  model: {response.model}")
        server_logger.info(f"  finish_reason: {response.choices[0].finish_reason}")

        result = json.loads(response.choices[0].message.content)
        server_logger.info("Parsed fields from transcript:")
        print("\n Successfully parsed voice transcript:")
        for key, value in result.items():
            server_logger.info(f"  - {key}: {value}")
            print(f"   {key}: {value}")
        server_logger.info("=" * 80)
        print("=" * 80)
        return result
        
    except json.JSONDecodeError as exc:
        server_logger.error(f"JSON decode failed: {exc}")
        server_logger.error(f"Raw message content: {response.choices[0].message.content if 'response' in locals() else 'N/A'}")
        server_logger.error("=" * 80)
        print(f"\n JSON decode error: {exc}")
        print(f"   Raw content: {response.choices[0].message.content if 'response' in locals() else 'N/A'}")
        raise HTTPException(status_code=500, detail="Failed to parse AI response as JSON")
    except Exception as exc:
        import traceback
        error_trace = traceback.format_exc()
        server_logger.error(f"Voice dictation error: {exc}")
        server_logger.error(error_trace)
        server_logger.error("=" * 80)
        print(f"\n Voice dictation error: {exc}")
        print(error_trace)
        print("=" * 80)
        raise HTTPException(status_code=500, detail=f"Failed to process voice input: {str(exc)}")


@app.post("/api/plan", response_model=PlanResponse)
async def create_plan(payload: EventRequest) -> PlanResponse:
    global _last_result_cache, _current_progress
    
    # Map incoming payload to the existing workflow schema
    event_details = map_request_to_workflow_payload(payload)

    # Set non-interactive mode and dev settings for API calls
    os.environ["EVENT_PLANNER_NON_INTERACTIVE"] = "1"
    os.environ["EVENT_PLANNER_ENABLE_SANDBOX"] = "1" if payload.enableSandbox else "0"
    os.environ["EVENT_PLANNER_ENABLE_SMS"] = "1" if payload.enableSMS else "0"
    
    # Initialize progress tracking
    _current_progress = {
        "phase": "phase_1",
        "phase_name": "Coordinator Planning",
        "status": "in_progress",
        "agents": [],
        "current_agent": None,
        "message": "Analyzing event requirements..."
    }
    
    # Run the long-running workflow in a worker thread to avoid blocking the loop
    try:
        # Create a thread-safe copy of progress tracker reference
        progress_ref = _current_progress
        result = await asyncio.to_thread(run_event_planning, event_details, progress_ref)
    except Exception as exc:  # noqa: BLE001 - surface full error to client
        _current_progress["status"] = "error"
        _current_progress["message"] = str(exc)
        import traceback
        print(f"\n  Workflow error: {exc}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(exc))

    response = PlanResponse(status="ok", event_details=event_details, result=result)
    
    # Log what's being sent to frontend
    print(f"\n SERVER: Sending response to frontend:")
    print(f"    event_schedule: {len(result.get('event_schedule', ''))} chars")
    print(f"    entertainment: {len(result.get('entertainment', ''))} chars")
    print(f"    event_schedule preview: {result.get('event_schedule', '')[:200]}...")
    print(f"    entertainment preview: {result.get('entertainment', '')[:200]}...")
    
    server_logger.info("="*80)
    server_logger.info("Response sent to frontend:")
    for key, value in result.items():
        length = len(str(value)) if value else 0
        server_logger.info(f"  {key}: {length} chars")
        if length > 0 and length < 1000:
            server_logger.debug(f"  {key} full content: {value}")
        elif length > 0:
            server_logger.debug(f"  {key} preview: {str(value)[:500]}...")
    
    server_logger.info("="*80)
    server_logger.info("Response sent to frontend:")
    for key, value in result.items():
        length = len(str(value)) if value else 0
        server_logger.info(f"  {key}: {length} chars")
        if length > 0 and length < 1000:
            server_logger.debug(f"  {key} full content: {value}")
        elif length > 0:
            server_logger.debug(f"  {key} preview: {str(value)[:500]}...")
    server_logger.info("="*80)
    
    # Cache the successful result
    _last_result_cache = response.model_dump()
    
    # Mark as complete and include final agent statuses
    _current_progress["status"] = "completed"
    _current_progress["phase"] = "complete"
    # Include final agent statuses from the result
    if result.get("agent_statuses"):
        _current_progress["agents"] = result["agent_statuses"]
    _current_progress["current_agent"] = None
    _current_progress["message"] = "Event planning completed successfully"
    
    server_logger.info("="*80)
    
    return response


@app.post("/api/refine-plan", response_model=RefinePlanResponse)
async def refine_plan(payload: RefinePlanRequest) -> RefinePlanResponse:
    """Refine an existing event plan based on user chat request.
    
    Only calls the necessary agents to make the requested changes,
    then regenerates the final plan with updates merged in.
    """
    global _current_progress
    
    server_logger.info("="*80)
    server_logger.info(" /api/refine-plan called")
    server_logger.info(f"User message: {payload.message}")
    server_logger.info(f"Changed sections expected: {payload.changed_sections if hasattr(payload, 'changed_sections') else 'N/A'}")
    print(f"\n /api/refine-plan endpoint called")
    print(f"   User message: {payload.message}")
    
    # Initialize progress tracking
    _current_progress = {
        "phase": "refinement",
        "phase_name": "Refining Plan",
        "status": "in_progress",
        "agents": [],
        "current_agent": None,
        "message": f"Analyzing your request: {payload.message[:50]}..."
    }
    
    try:
        # Run refinement in a worker thread with timeout (5 minutes max)
        result = await asyncio.wait_for(
            asyncio.to_thread(
                refine_event_plan,
                current_plan=payload.current_plan,
                specialist_outputs=payload.specialist_outputs,
                user_message=payload.message,
                event_details=payload.event_details,
                required_agents=payload.required_agents
            ),
            timeout=300.0  # 5 minutes timeout
        )
        
        # Update progress
        _current_progress["status"] = "completed"
        _current_progress["phase"] = "complete"
        _current_progress["message"] = f"Updated {', '.join(result.get('changed_sections', []))} based on your request"
        
        server_logger.info(" Refinement completed successfully")
        server_logger.info(f"   Changed sections: {result.get('changed_sections', [])}")
        server_logger.info(f"   Agents called: {result.get('agents_called', [])}")
        print(f" Refinement completed")
        print(f"   Changed sections: {result.get('changed_sections', [])}")
        print(f"   Agents called: {result.get('agents_called', [])}")
        
        return RefinePlanResponse(
            updated_plan=result.get("updated_plan", payload.current_plan),
            changed_sections=result.get("changed_sections", []),
            agents_called=result.get("agents_called", []),
            coordinator_message=result.get("coordinator_message", "Plan updated successfully"),
            error=result.get("error")
        )
        
    except asyncio.TimeoutError:
        _current_progress["status"] = "error"
        _current_progress["message"] = "Refinement timed out after 5 minutes"
        server_logger.error(" Refinement timed out")
        print("\n Refinement timed out after 5 minutes")
        raise HTTPException(status_code=504, detail="Refinement request timed out. Please try again with a more specific request.")
    except Exception as exc:
        _current_progress["status"] = "error"
        _current_progress["message"] = str(exc)
        import traceback
        error_trace = traceback.format_exc()
        server_logger.error(f" Refinement error: {exc}")
        server_logger.error(error_trace)
        print(f"\n Refinement error: {exc}")
        print(error_trace)
        raise HTTPException(status_code=500, detail=f"Failed to refine plan: {str(exc)}")


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
