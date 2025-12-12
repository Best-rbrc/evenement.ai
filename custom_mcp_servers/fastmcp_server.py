"""FastMCP server exposing the event planner workflow.

This server provides MCP tools for planning events using the AI Event Planner Agent.
It runs the workflow in non-interactive mode by default, making it suitable for
headless/automated use cases.

Tools:
- plan_event: Run the full event planning workflow and return results
- list_event_outputs: List all generated files in event_outputs/
- read_event_output: Read the contents of a specific output file

Environment Variables:
- OPENAI_API_KEY: Required - Your OpenAI API key
- TALLY_API_KEY: Optional - For form creation (if PLAN_EVENT_FORM_MODE=unsandboxed)
- PLAN_EVENT_FORM_MODE: Optional - "skip" (default), "sandboxed", or "unsandboxed"

Example Usage:
    event_details = {
        "event_name": "Tech Conference 2024",
        "event_type": "conference",
        "event_date": "2024-06-15",
        "location_preference": "San Francisco, CA",
        "budget_range": "$50,000-$75,000",
        "guest_count": "200-300",
        "special_requirements": "Accessible venue, vegetarian options"
    }
    result = await plan_event(event_details)
"""
from __future__ import annotations

import asyncio
import argparse
import base64
import builtins
import logging
import os
import sys
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from dotenv import load_dotenv

from workflows import event_planning_workflow
from workflows.event_planning_workflow import PROJECT_OUTPUT_DIR, run_event_planning

# Defaults to keep workflow non-interactive when called via MCP
# Use unsandboxed/no-form path by default to avoid container startup in headless runs.
_DEFAULT_FORM_CHOICE = "2"  # 1 = sandboxed local Tally MCP, 2 = unsandboxed/skip sandbox
_DEFAULT_SMS_CHOICE = "no"  # skip SMS sending
_OUTPUT_DIR = PROJECT_OUTPUT_DIR

# Load environment variables from .env (OPENAI_API_KEY, TALLY_API_KEY, etc.)
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

server = FastMCP("event-planner")


def _run_workflow_headless(event_details: dict[str, Any]) -> dict[str, Any]:
    """Run workflow with patched input so it stays non-interactive."""
    # Always feed deterministic answers: first form choice, then SMS choice,
    # then stick to the SMS default for any further prompts.
    answers = [_DEFAULT_FORM_CHOICE, _DEFAULT_SMS_CHOICE]
    original_input = builtins.input

    def _patched_input(_prompt: str = "") -> str:
        if answers:
            return answers.pop(0)
        return _DEFAULT_SMS_CHOICE

    builtins.input = _patched_input

    # Configure sandbox + forms based on env flag (default: skip for clean MCP runs)
    mode = os.getenv("PLAN_EVENT_FORM_MODE", "skip").lower()
    # modes: skip (default, no forms) | sandboxed (Docker+Tally) | unsandboxed (direct Tally API)
    if mode == "sandboxed":
        event_planning_workflow.SKIP_FORM_CREATION = False
        event_planning_workflow.USE_SANDBOXED_FORMS = True
        event_planning_workflow.SANDBOX_ENABLED = True
    elif mode == "unsandboxed":
        event_planning_workflow.SKIP_FORM_CREATION = False
        event_planning_workflow.USE_SANDBOXED_FORMS = False
        event_planning_workflow.SANDBOX_ENABLED = False
    else:  # skip
        event_planning_workflow.SKIP_FORM_CREATION = True
        event_planning_workflow.USE_SANDBOXED_FORMS = False
        event_planning_workflow.SANDBOX_ENABLED = False

    try:
        return run_event_planning(event_details)
    finally:
        builtins.input = original_input


@server.tool()
async def plan_event(event_details: dict[str, Any]) -> dict[str, Any]:
    """Run the event planner workflow and return comprehensive results.
    
    Args:
        event_details: Dictionary containing event information. Required fields:
            - event_name (str): Name of the event
            - event_type (str): Type of event (e.g., "conference", "wedding", "corporate")
        Optional fields:
            - event_date (str): Event date (YYYY-MM-DD or date range)
            - location_preference (str): Preferred location
            - budget_range (str): Budget range (e.g., "$10,000-$20,000")
            - guest_count (str): Expected guest count (e.g., "100-150")
            - special_requirements (str): Any special requirements or constraints
    
    Returns:
        Dictionary with:
            - status: "success" or "error"
            - calendar_file_path: Path to generated ICS calendar file (if created)
            - form_url: URL to registration form (if created)
            - pdf_path: Path to generated PDF report (if created)
            - logo_path: Path to generated logo file (if created)
            - final_plan: Complete event plan with all recommendations
            - agents_used: List of agents that were used
            - success: Boolean indicating if planning succeeded
            - error: Error message if status is "error"
    
    Raises:
        ValueError: If required fields are missing or event_details is not a dict
        RuntimeError: If the workflow execution fails
    """
    if not isinstance(event_details, dict):
        raise ValueError("event_details must be a dictionary")

    # Validate required fields
    required = ["event_name", "event_type"]
    missing = [key for key in required if not event_details.get(key)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    try:
        logger.info(f"Starting event planning for: {event_details.get('event_name', 'Unknown')}")
        result = await asyncio.to_thread(_run_workflow_headless, event_details)
        
        # Extract file paths and URLs from the result structure
        calendar_data = result.get("calendar_invite", {})
        if isinstance(calendar_data, dict):
            calendar_file = calendar_data.get("calendar_file_path")
        else:
            calendar_file = None
        
        form_data = result.get("registration_form", {})
        if isinstance(form_data, dict):
            form_url = form_data.get("form_url")
        else:
            form_url = None
        
        pdf_path = result.get("pdf_report")
        
        logo_data = result.get("logo", {})
        if isinstance(logo_data, dict):
            logo_path = logo_data.get("logo_file_path") or logo_data.get("logo_url")
        else:
            logo_path = None
        
        # Build response
        response = {
            "status": "success" if result.get("success", False) else "error",
            "calendar_file_path": calendar_file,
            "form_url": form_url,
            "pdf_path": pdf_path,
            "logo_path": logo_path,
            "final_plan": result.get("final_plan", {}),
            "agents_used": result.get("agents_used", []),
            "success": result.get("success", False),
        }
        
        # Include error message if present
        if not result.get("success", False):
            response["error"] = "Event planning workflow completed with errors"
        
        logger.info(f"Event planning completed: {response['status']}")
        return response
        
    except Exception as e:
        logger.error(f"Event planning failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "success": False,
            "calendar_file_path": None,
            "form_url": None,
            "pdf_path": None,
            "logo_path": None,
            "final_plan": {},
            "agents_used": [],
        }


@server.tool()
async def list_event_outputs() -> list[dict[str, str]]:
    """List all files produced in the event_outputs/ directory.
    
    Returns:
        List of dictionaries, each containing:
            - name: File name
            - path: Absolute file path
            - size_bytes: File size in bytes (as string)
            - file_type: Inferred file type based on extension (e.g., "ics", "pdf", "png")
    
    Note:
        This only lists files directly in event_outputs/, not subdirectories.
    """
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    items: list[dict[str, str]] = []
    for path in sorted(_OUTPUT_DIR.glob("*")):
        if path.is_file():
            # Infer file type from extension
            file_type = path.suffix.lstrip(".").lower() if path.suffix else "unknown"
            
            items.append({
                "name": path.name,
                "path": str(path.resolve()),
                "size_bytes": str(path.stat().st_size),
                "file_type": file_type,
            })
    return items


@server.tool()
async def read_event_output(file_name: str) -> dict[str, Any]:
    """Read the contents of a specific output file.
    
    Args:
        file_name: Name of the file to read (must be in event_outputs/ directory).
                  Path separators are not allowed for security.
    
    Returns:
        Dictionary containing:
            - name: File name
            - content_type: "text" for text files, "base64" for binary files
            - content: File contents (as string for text, base64-encoded for binary)
            - size_bytes: File size in bytes
    
    Raises:
        ValueError: If file_name contains path separators
        FileNotFoundError: If the file doesn't exist
    
    Note:
        Text files (ICS, JSON, etc.) are returned as-is. Binary files (PDF, PNG, etc.)
        are base64-encoded. Large files may cause performance issues.
    """
    safe_name = Path(file_name).name
    if safe_name != file_name:
        raise ValueError("file_name must not contain path separators (use only the filename)")

    path = _OUTPUT_DIR / safe_name
    if not path.exists():
        available_files = [f.name for f in _OUTPUT_DIR.glob("*") if f.is_file()]
        raise FileNotFoundError(
            f"No such output file: {file_name}. "
            f"Available files: {', '.join(available_files[:10])}"
            + (f" (and {len(available_files) - 10} more)" if len(available_files) > 10 else "")
        )
    
    if not path.is_file():
        raise ValueError(f"{file_name} exists but is not a file")

    file_size = path.stat().st_size
    
    # Try to read as text first (for ICS, JSON, TXT, etc.)
    try:
        content = path.read_text(encoding="utf-8")
        return {
            "name": safe_name,
            "content_type": "text",
            "content": content,
            "size_bytes": file_size,
        }
    except UnicodeDecodeError:
        # Binary file - encode as base64
        data = path.read_bytes()
        encoded = base64.b64encode(data).decode("ascii")
        return {
            "name": safe_name,
            "content_type": "base64",
            "content": encoded,
            "size_bytes": file_size,
        }


def serve():
    """CLI entrypoint for running the FastMCP server.
    
    This function starts the MCP server and makes it available for MCP clients
    to connect to. The server will listen for tool calls and execute them.
    
    Usage:
        python -m custom_mcp_servers.fastmcp_server
        # or
        event-planner-mcp  # if installed as a script
    """
    parser = argparse.ArgumentParser(
        description="AI Event Planner MCP Server - Plan events using specialized AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start the server (for MCP clients)
  event-planner-mcp
  
  # Start with custom form mode
  PLAN_EVENT_FORM_MODE=unsandboxed event-planner-mcp

Environment Variables:
  OPENAI_API_KEY       Required - Your OpenAI API key
  TALLY_API_KEY        Optional - For form creation (if PLAN_EVENT_FORM_MODE=unsandboxed)
  PLAN_EVENT_FORM_MODE Optional - "skip" (default), "unsandboxed", or "sandboxed"
  
For more information, see: https://github.com/Adrien-Z/AI-Event-Planner-Agent
        """
    )
    parser.add_argument(
        "--version",
        action="version",
        version="event-planner-mcp 1.0.0"
    )
    
    # Parse arguments (but MCP servers don't typically use CLI args, just --help)
    args = parser.parse_args()
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not set. The server may not work correctly.", file=sys.stderr)
        print("Set it with: export OPENAI_API_KEY='sk-proj-...'", file=sys.stderr)
    
    logger.info("Starting FastMCP Event Planner server...")
    logger.info(f"Output directory: {_OUTPUT_DIR}")
    logger.info(f"Form mode: {os.getenv('PLAN_EVENT_FORM_MODE', 'skip')}")
    server.run()


if __name__ == "__main__":
    serve()
