"""Utility functions for event planning workflow."""
import datetime
import shutil
import time
import re
import random
from typing import Dict, Any
from pathlib import Path
from agents import Runner


def get_current_date_context() -> str:
    """Get current date context for agents."""
    current_date = datetime.datetime.now()
    return f"Today's date: {current_date.strftime('%B %d, %Y')} ({current_date.strftime('%Y-%m-%d')})"


def copy_sandbox_files_to_project(sandbox_dir: Path, project_output_dir: Path):
    """Copy files from sandbox temp directory to project directory.
    
    Args:
        sandbox_dir: Path to sandbox directory
        project_output_dir: Path to project output directory
    """
    if not sandbox_dir.exists():
        return
    
    copied_count = 0
    for file in sandbox_dir.glob("*"):
        if file.is_file():
            dest = project_output_dir / file.name
            shutil.copy2(file, dest)
            copied_count += 1
    
    if copied_count > 0:
        print(f" Copied {copied_count} file(s) from sandbox to {project_output_dir}")


def create_basic_schedule(event_details: Dict[str, Any]) -> Dict[str, Any]:
    """Create a basic schedule from event details when no schedule is provided by agents.
    
    Args:
        event_details: Event information dict
        
    Returns:
        Basic schedule dict with sessions
    """
    event_name = event_details.get('event_name', 'Event')
    event_date = event_details.get('event_date', '')
    time_window = event_details.get('time_window', '09:00 - 17:00')
    guest_count = event_details.get('guest_count', 'TBD')
    
    # Parse time window
    start_time = '09:00'
    end_time = '17:00'
    if ' - ' in time_window:
        times = time_window.split(' - ')
        if len(times) == 2:
            start_time = times[0].strip()
            end_time = times[1].strip()
    
    # Parse event dates for multi-day events
    event_dates = []
    if event_date:
        if ' to ' in event_date:
            event_dates = [d.strip() for d in event_date.split(' to ')]
        else:
            event_dates = [event_date]
    
    # Create basic sessions
    sessions = []
    
    # For single-day events, create one main session
    if len(event_dates) <= 1:
        date = event_dates[0] if event_dates else event_date
        sessions.append({
            "session_id": 1,
            "name": event_name,
            "start_time": start_time,
            "end_time": end_time,
            "duration": 480,  # 8 hours default
            "date": date if date else None
        })
    else:
        # For multi-day events, create one session per day
        for idx, date in enumerate(event_dates):
            sessions.append({
                "session_id": idx + 1,
                "name": f"{event_name} - Day {idx + 1}",
                "start_time": start_time,
                "end_time": end_time,
                "duration": 480,
                "date": date
            })
    
    return {
        "optimized": False,
        "sessions": sessions,
        "status": "basic"
    }


def run_sync_with_backoff(agent, prompt, max_turns: int = 20, max_retries: int = 3):
    """Run agent with rate-limit aware retries.
    
    Args:
        agent: The agent to run
        prompt: The prompt to send
        max_turns: Maximum number of turns for the agent
        max_retries: Maximum number of retry attempts
        
    Returns:
        Agent result
        
    Raises:
        Exception: If all retries fail
    """
    last_exc = None
    for attempt in range(max_retries):
        try:
            return Runner.run_sync(agent, prompt, max_turns=max_turns)
        except Exception as e:
            last_exc = e
            msg = str(e)
            if "rate_limit_exceeded" in msg or "Please try again in" in msg:
                # Parse suggested wait, else exponential backoff
                wait_time = 2 ** attempt
                m = re.search(r"Please try again in\s+([0-9]+\.?[0-9]*)s", msg)
                if m:
                    try:
                        wait_time = float(m.group(1))
                    except Exception:
                        pass
                wait_time += random.uniform(0.3, 0.7)
                print(f"⏳ Rate limit. Waiting {wait_time:.2f}s before retry...\n")
                time.sleep(wait_time)
                continue
            else:
                break
    raise last_exc

