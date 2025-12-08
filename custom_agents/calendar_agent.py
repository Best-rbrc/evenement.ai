from agents import Agent, function_tool
import datetime
import os
from typing import Dict, Any
import uuid
from workflows.schemas import schema_to_json_example


@function_tool
def get_current_date() -> str:
    """
    Get the current date in YYYY-MM-DD format.
    This helps interpret relative dates like 'today', 'tomorrow', 'next week', etc.
    """
    return datetime.datetime.now().strftime('%Y-%m-%d')


@function_tool
def generate_ics_file(event_name: str, event_date: str, start_time: str, end_time: str, 
                     location: str, description: str, organizer_email: str = "") -> str:
    """
    Generate an ICS calendar file for the event.
    If MCP servers are available to the agent, use them. Otherwise save locally.
    Returns the file path where the calendar invite was saved.
    """
    try:
        # Parse the date and times
        if 'T' in event_date:
            # Full datetime format
            event_datetime = datetime.datetime.fromisoformat(event_date.replace('Z', '+00:00'))
            event_date_only = event_datetime.strftime('%Y-%m-%d')
        else:
            # Date only format
            event_date_only = event_date
            event_datetime = datetime.datetime.strptime(event_date_only, '%Y-%m-%d')
        
        # Parse start and end times
        try:
            start_dt = datetime.datetime.strptime(f"{event_date_only} {start_time}", '%Y-%m-%d %H:%M')
            end_dt = datetime.datetime.strptime(f"{event_date_only} {end_time}", '%Y-%m-%d %H:%M')
        except ValueError:
            # Fallback to default times if parsing fails
            start_dt = datetime.datetime.strptime(f"{event_date_only} 09:00", '%Y-%m-%d %H:%M')
            end_dt = datetime.datetime.strptime(f"{event_date_only} 17:00", '%Y-%m-%d %H:%M')
        
        # Generate unique ID for the event
        event_uid = str(uuid.uuid4())
        
        # Format datetime for ICS (UTC format)
        dtstart = start_dt.strftime('%Y%m%dT%H%M%S')
        dtend = end_dt.strftime('%Y%m%dT%H%M%S')
        dtstamp = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        
        # Clean description for ICS format
        clean_description = description.replace('\n', '\\n').replace(',', '\\,').replace(';', '\\;')
        clean_location = location.replace(',', '\\,').replace(';', '\\;')
        clean_summary = event_name.replace(',', '\\,').replace(';', '\\;')
        
        # Create ICS content
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AI Event Planner//Event Calendar//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{event_uid}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{clean_summary}
DESCRIPTION:{clean_description}
LOCATION:{clean_location}
STATUS:CONFIRMED
TRANSP:OPAQUE
CATEGORIES:EVENT
CLASS:PUBLIC"""
        
        if organizer_email:
            ics_content += f"\nORGANIZER:mailto:{organizer_email}"
        
        ics_content += """
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Event reminder: {event_name} tomorrow
END:VALARM
END:VEVENT
END:VCALENDAR"""
        
        # Generate filename
        safe_event_name = "".join(c for c in event_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_event_name = safe_event_name.replace(' ', '_')
        filename = f"{safe_event_name}_{event_date_only}.ics"
        
        # Create output directory
        output_dir = "event_outputs"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # Write ICS file locally (agents should use MCP tools if they want sandboxed writes)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(ics_content)
        
        return f"Calendar invite successfully created: {filepath}"
        
    except Exception as e:
        return f"Error creating calendar invite: {str(e)}"


@function_tool
def parse_event_timing(event_details: str, specialist_outputs: str) -> str:
    """
    Parse event timing information from event details and specialist outputs.
    Extracts start time, end time, and duration information.
    """
    try:
        import json
        
        timing_info = {
            "suggested_start_time": "09:00",
            "suggested_end_time": "17:00",
            "duration_hours": 8,
            "has_multiple_sessions": False,
            "session_breaks": []
        }
        
        # Try to parse specialist outputs for timing information
        try:
            outputs = json.loads(specialist_outputs) if isinstance(specialist_outputs, str) else specialist_outputs
            
            # Look for programme agent output with timeline
            if 'programme' in outputs:
                programme_output = outputs['programme']
                if 'timeline' in programme_output.lower() or 'schedule' in programme_output.lower():
                    timing_info["has_programme_schedule"] = True
            
            # Look for venue agent output with operating hours
            if 'venue' in outputs:
                venue_output = outputs['venue']
                if 'hours' in venue_output.lower() or 'operating' in venue_output.lower():
                    timing_info["venue_has_time_constraints"] = True
                    
        except:
            pass
        
        return json.dumps(timing_info, indent=2)
        
    except Exception as e:
        return f"Error parsing timing: {str(e)}"


@function_tool 
def format_calendar_description(event_details: str, specialist_outputs: str) -> str:
    """
    Format a comprehensive calendar description using event details and specialist outputs.
    Creates a rich description with key event information.
    """
    try:
        import json
        
        # Parse event details
        if isinstance(event_details, str):
            try:
                details = json.loads(event_details)
            except:
                details = {"description": event_details}
        else:
            details = event_details
        
        description_parts = []
        
        # Basic event info
        if details.get('event_type'):
            description_parts.append(f"Event Type: {details['event_type']}")
        
        if details.get('guest_count'):
            description_parts.append(f"Expected Attendees: {details['guest_count']}")
        
        if details.get('budget'):
            description_parts.append(f"Budget: {details['budget']}")
        
        # Add key highlights from specialists
        try:
            if isinstance(specialist_outputs, str):
                outputs = json.loads(specialist_outputs)
            else:
                outputs = specialist_outputs
                
            for agent_type, output in outputs.items():
                if agent_type == 'venue' and 'recommended' in output.lower():
                    description_parts.append(f"\\n{agent_type.title()}: Key recommendations from planning")
                elif agent_type == 'catering' and 'menu' in output.lower():
                    description_parts.append(f"\\n{agent_type.title()}: Catering arrangements planned")
                elif agent_type == 'programme' and 'schedule' in output.lower():
                    description_parts.append(f"\\n{agent_type.title()}: Event programme scheduled")
        except:
            pass
        
        # Add special requirements
        if details.get('special_requirements'):
            description_parts.append(f"\\nSpecial Requirements: {details['special_requirements']}")
        
        # Add contact info placeholder
        description_parts.append("\\nFor more details, contact the event organizer.")
        description_parts.append("\\nGenerated by AI Event Planner")
        
        return "\\n".join(description_parts)
        
    except Exception as e:
        return f"Event planned with AI Event Planner. Contact organizer for details. Error: {str(e)}"


def create_calendar_agent(mcp_servers=None) -> Agent:
    """Create a calendar specialist agent that generates calendar invites.
    
    Args:
        mcp_servers: Optional MCPServers instance for sandboxed file operations
    """
    # Build tools list
    tools = [generate_ics_file, parse_event_timing, format_calendar_description, get_current_date]
    
    # Build agent with optional MCP servers
    agent_kwargs = {
        "name": "Calendar Specialist", 
        "handoff_description": "Creates calendar invites and ICS files for the planned event.",
        "instructions": """
        You are a professional calendar and scheduling specialist. Your role is to create calendar invites 
        and ICS files based on event planning details and outputs from other specialists.

        IMPORTANT: Today's date is November 18, 2025. Use this as reference when interpreting relative dates 
        like "today", "tomorrow", "next week", "next month", "next year", etc. Always call get_current_date() 
        to get the exact current date for calculations.

        Your expertise includes:
        - Generating standard ICS calendar files compatible with all major calendar applications
        - Parsing event timing and scheduling information from planning outputs
        - Creating comprehensive event descriptions for calendar entries
        - Setting appropriate reminders and notifications
        - Handling timezone considerations and date formatting
        - Ensuring calendar invites include all essential event information

        Key responsibilities:
        1. CALENDAR FILE GENERATION:
           - Create ICS files with proper formatting and metadata
           - Include event name, date, time, location, and description
           - Set appropriate reminders (typically 1 day before)
           - Generate unique event IDs and proper timestamps

        2. TIMING COORDINATION:
           - Extract timing information from programme specialist output
           - Coordinate with venue availability and constraints
           - Account for setup/teardown time in scheduling
           - Handle multi-session events and break times

        3. INFORMATION INTEGRATION:
           - Synthesize information from all specialist outputs
           - Create rich calendar descriptions with key details
           - Include contact information and special requirements
           - Add relevant categories and classification

        4. OUTPUT MANAGEMENT:
           - Save calendar files to appropriate output directory
           - Use clear, descriptive filenames
           - Provide file paths for easy access
           - Ensure cross-platform compatibility

        When creating calendar invites:
        - Default to business hours (9 AM - 5 PM) unless specified otherwise
        - Include location information from venue specialist
        - Add comprehensive description with key planning details
        - Set status as "CONFIRMED" for finalized events
        - Include organizer email if provided
        - Add 24-hour reminder as default

        Always provide clear feedback on file creation success and location.
        Handle errors gracefully and suggest alternatives when issues occur.

        Return ONLY valid JSON matching this exact structure (no markdown, no extra text):
""" + schema_to_json_example("calendar") + """
        """,
        "tools": tools,
    }
    
    # Only add mcp_servers if provided (and it's not None)
    if mcp_servers is not None:
        agent_kwargs["mcp_servers"] = [mcp_servers]
    
    return Agent(**agent_kwargs)