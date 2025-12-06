"""FastMCP server exposing the event planner workflow.

Tools:
- plan_event: run the full event planning workflow (non-interactive defaults)
- list_event_outputs: enumerate generated files in event_outputs/
- read_event_output: return file content for small/text outputs
"""
from __future__ import annotations

import asyncio
import base64
import builtins
import os
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
    """Run the event planner and return key artifact paths/urls."""
    if not isinstance(event_details, dict):
        raise ValueError("event_details must be an object")

    required = ["event_name", "event_type"]
    missing = [key for key in required if not event_details.get(key)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    result = await asyncio.to_thread(_run_workflow_headless, event_details)

    calendar_file = result.get("calendar_file_path") or result.get("calendar", {}).get("calendar_file_path")
    form_url = result.get("form_url") or result.get("form", {}).get("form_url")
    pdf_path = result.get("pdf_path") or result.get("pdf")

    return {
        "status": "success",
        "calendar_file_path": calendar_file,
        "form_url": form_url,
        "pdf_path": pdf_path,
        "raw_result": result,
    }


@server.tool()
async def list_event_outputs() -> list[dict[str, str]]:
    """List files produced in event_outputs/ (ICS/PDF/etc)."""
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    items: list[dict[str, str]] = []
    for path in sorted(_OUTPUT_DIR.glob("*")):
        if path.is_file():
            items.append({
                "name": path.name,
                "path": str(path.resolve()),
                "size_bytes": str(path.stat().st_size),
            })
    return items


@server.tool()
async def read_event_output(file_name: str) -> dict[str, Any]:
    """Return contents for a specific output file. Text is returned directly; binary is base64."""
    safe_name = Path(file_name).name
    if safe_name != file_name:
        raise ValueError("file_name must not contain path separators")

    path = _OUTPUT_DIR / safe_name
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"No such output file: {file_name}")

    # Heuristic: treat small/text files as text, others as base64
    try:
        content = path.read_text()
        return {"name": safe_name, "content_type": "text", "content": content}
    except UnicodeDecodeError:
        data = path.read_bytes()
        encoded = base64.b64encode(data).decode("ascii")
        return {"name": safe_name, "content_type": "base64", "content": encoded}


def serve():
    """CLI entrypoint for pyproject script."""
    server.run()


if __name__ == "__main__":
    serve()
