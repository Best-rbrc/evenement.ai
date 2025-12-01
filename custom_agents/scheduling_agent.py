"""Advanced scheduling agent with constraint optimization using Google OR-Tools."""
from agents import Agent, function_tool
from ortools.sat.python import cp_model
from typing import List, Dict, Any, Tuple
import json
from datetime import datetime, timedelta


def parse_time_to_minutes(time_str: str) -> int:
    """Convert time string (HH:MM) to minutes since midnight."""
    try:
        h, m = map(int, time_str.split(':'))
        return h * 60 + m
    except:
        return 0


def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to time string (HH:MM)."""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


@function_tool
def optimize_schedule(
    sessions: str,
    rooms: str,
    speakers: str,
    constraints: str
) -> str:
    """
    Optimize event schedule using constraint programming with Google OR-Tools.
    
    Args:
        sessions: JSON string of sessions [{"id": 1, "name": "...", "duration": 60, "speaker": "A", "expected_attendees": 50}]
        rooms: JSON string of rooms [{"id": 1, "name": "...", "capacity": 100, "equipment": [...]}]
        speakers: JSON string of speakers [{"id": "A", "name": "...", "travel_time_minutes": 0}]
        constraints: JSON string of constraints {"event_start": "09:00", "event_end": "18:00", "lunch_break": "12:00-13:00", ...}
    
    Returns:
        JSON string with optimized schedule or explanation if infeasible
    """
    try:
        # Parse inputs
        sessions_data = json.loads(sessions) if isinstance(sessions, str) else sessions
        rooms_data = json.loads(rooms) if isinstance(rooms, str) else rooms
        speakers_data = json.loads(speakers) if isinstance(speakers, str) else speakers
        constraints_data = json.loads(constraints) if isinstance(constraints, str) else constraints
        
        # Validate inputs
        if not sessions_data or not rooms_data:
            return json.dumps({
                "status": "error",
                "message": "Sessions and rooms are required"
            })
        
        # Create model
        model = cp_model.CpModel()
        
        # Time bounds (in minutes from event start)
        event_start = parse_time_to_minutes(constraints_data.get('event_start', '09:00'))
        event_end = parse_time_to_minutes(constraints_data.get('event_end', '18:00'))
        total_minutes = event_end - event_start
        
        # Parse lunch break
        lunch_start = None
        lunch_end = None
        if 'lunch_break' in constraints_data:
            lunch_times = constraints_data['lunch_break'].split('-')
            if len(lunch_times) == 2:
                lunch_start = parse_time_to_minutes(lunch_times[0]) - event_start
                lunch_end = parse_time_to_minutes(lunch_times[1]) - event_start
        
        # Create variables: when does each session start?
        session_starts = {}
        session_ends = {}
        session_intervals = {}
        
        for session in sessions_data:
            sid = session['id']
            duration = session.get('duration', 60)
            
            start_var = model.NewIntVar(0, total_minutes - duration, f'start_{sid}')
            end_var = model.NewIntVar(duration, total_minutes, f'end_{sid}')
            interval_var = model.NewIntervalVar(start_var, duration, end_var, f'interval_{sid}')
            
            session_starts[sid] = start_var
            session_ends[sid] = end_var
            session_intervals[sid] = interval_var
        
        # Create variables: which room for each session?
        session_rooms = {}
        room_intervals = {room['id']: [] for room in rooms_data}
        
        for session in sessions_data:
            sid = session['id']
            
            # Create boolean variables for each room assignment
            room_bools = []
            for room in rooms_data:
                rid = room['id']
                bool_var = model.NewBoolVar(f'session_{sid}_room_{rid}')
                room_bools.append(bool_var)
                
                # If this session is in this room, add its interval
                # We create an optional interval
                optional_interval = model.NewOptionalIntervalVar(
                    session_starts[sid],
                    session.get('duration', 60),
                    session_ends[sid],
                    bool_var,
                    f'optional_{sid}_{rid}'
                )
                room_intervals[rid].append(optional_interval)
            
            # Each session must be in exactly one room
            model.Add(sum(room_bools) == 1)
            session_rooms[sid] = room_bools
        
        # CONSTRAINT 1: No room can host multiple sessions simultaneously
        for rid, intervals in room_intervals.items():
            if intervals:
                model.AddNoOverlap(intervals)
        
        # CONSTRAINT 2: Room capacity must accommodate expected attendees
        for session in sessions_data:
            sid = session['id']
            expected = session.get('expected_attendees', 0)
            
            if expected > 0:
                for i, room in enumerate(rooms_data):
                    capacity = room.get('capacity', 999999)
                    if expected > capacity:
                        # This room cannot host this session
                        model.Add(session_rooms[sid][i] == 0)
        
        # CONSTRAINT 3: No speaker in two places at once
        speaker_map = {}
        for session in sessions_data:
            speaker = session.get('speaker', '')
            if speaker:
                if speaker not in speaker_map:
                    speaker_map[speaker] = []
                speaker_map[speaker].append(session['id'])
        
        for speaker, session_ids in speaker_map.items():
            if len(session_ids) > 1:
                # Get travel time for this speaker
                speaker_info = next((s for s in speakers_data if s.get('id') == speaker or s.get('name') == speaker), {})
                travel_time = speaker_info.get('travel_time_minutes', 30)
                
                # No two sessions by same speaker can overlap (with buffer)
                intervals_for_speaker = [session_intervals[sid] for sid in session_ids]
                model.AddNoOverlap(intervals_for_speaker)
                
                # Add travel time buffer between sessions
                for i in range(len(session_ids) - 1):
                    for j in range(i + 1, len(session_ids)):
                        sid1, sid2 = session_ids[i], session_ids[j]
                        # Either session1 ends + travel_time before session2 starts
                        # Or session2 ends + travel_time before session1 starts
                        b = model.NewBoolVar(f'order_{sid1}_{sid2}')
                        model.Add(session_ends[sid1] + travel_time <= session_starts[sid2]).OnlyEnforceIf(b)
                        model.Add(session_ends[sid2] + travel_time <= session_starts[sid1]).OnlyEnforceIf(b.Not())
        
        # CONSTRAINT 4: Lunch break - no sessions during lunch
        if lunch_start is not None and lunch_end is not None:
            for session in sessions_data:
                sid = session['id']
                # Session must either end before lunch or start after lunch
                b = model.NewBoolVar(f'before_lunch_{sid}')
                model.Add(session_ends[sid] <= lunch_start).OnlyEnforceIf(b)
                model.Add(session_starts[sid] >= lunch_end).OnlyEnforceIf(b.Not())
        
        # CONSTRAINT 5: Keynote/important sessions in specific rooms
        for session in sessions_data:
            sid = session['id']
            preferred_room = session.get('preferred_room')
            
            if preferred_room:
                # Find room index
                for i, room in enumerate(rooms_data):
                    if room.get('name') == preferred_room or room.get('id') == preferred_room:
                        # Strongly prefer this room (soft constraint via objective bonus)
                        model.Add(session_rooms[sid][i] == 1)
                        break
        
        # OBJECTIVE: Minimize total event duration (compact schedule)
        max_end_time = model.NewIntVar(0, total_minutes, 'max_end_time')
        for sid in session_ends:
            model.Add(max_end_time >= session_ends[sid])
        
        model.Minimize(max_end_time)
        
        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        solver.parameters.log_search_progress = False
        
        status = solver.Solve(model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract solution
            schedule = []
            room_usage = {room['id']: [] for room in rooms_data}
            
            for session in sessions_data:
                sid = session['id']
                start_minutes = solver.Value(session_starts[sid])
                end_minutes = solver.Value(session_ends[sid])
                
                # Find assigned room
                assigned_room = None
                for i, room in enumerate(rooms_data):
                    if solver.Value(session_rooms[sid][i]) == 1:
                        assigned_room = room
                        room_usage[room['id']].append((start_minutes, end_minutes))
                        break
                
                actual_start_time = event_start + start_minutes
                actual_end_time = event_start + end_minutes
                
                schedule.append({
                    "session_id": session['id'],
                    "session_name": session.get('name', f"Session {sid}"),
                    "start_time": minutes_to_time(actual_start_time),
                    "end_time": minutes_to_time(actual_end_time),
                    "duration_minutes": session.get('duration', 60),
                    "room": assigned_room['name'] if assigned_room else "Unassigned",
                    "room_capacity": assigned_room.get('capacity', 0) if assigned_room else 0,
                    "speaker": session.get('speaker', 'TBD'),
                    "expected_attendees": session.get('expected_attendees', 0)
                })
            
            # Sort by start time
            schedule.sort(key=lambda x: x['start_time'])
            
            # Calculate metrics
            total_duration = solver.Value(max_end_time)
            room_utilization = {}
            for rid, usage in room_usage.items():
                if usage:
                    total_used = sum(end - start for start, end in usage)
                    utilization = (total_used / total_minutes) * 100
                    room_name = next((r['name'] for r in rooms_data if r['id'] == rid), f"Room {rid}")
                    room_utilization[room_name] = f"{utilization:.1f}%"
            
            return json.dumps({
                "status": "optimal" if status == cp_model.OPTIMAL else "feasible",
                "schedule": schedule,
                "metrics": {
                    "total_duration_minutes": total_duration,
                    "total_duration": f"{total_duration // 60}h {total_duration % 60}m",
                    "event_ends_at": minutes_to_time(event_start + total_duration),
                    "number_of_sessions": len(sessions_data),
                    "room_utilization": room_utilization,
                    "conflicts_resolved": "All constraints satisfied"
                },
                "summary": f"Successfully scheduled {len(sessions_data)} sessions across {len(rooms_data)} rooms"
            }, indent=2)
        
        elif status == cp_model.INFEASIBLE:
            # Identify potential conflicts
            conflicts = []
            
            # Check speaker overload
            for speaker, session_ids in speaker_map.items():
                total_duration = sum(s.get('duration', 60) for s in sessions_data if s['id'] in session_ids)
                if total_duration > total_minutes:
                    conflicts.append(f"Speaker '{speaker}' has {total_duration} minutes of sessions but only {total_minutes} minutes available")
            
            # Check room capacity issues
            for session in sessions_data:
                expected = session.get('expected_attendees', 0)
                suitable_rooms = [r for r in rooms_data if r.get('capacity', 0) >= expected]
                if not suitable_rooms:
                    conflicts.append(f"Session '{session.get('name', session['id'])}' needs {expected} capacity but no room is large enough")
            
            return json.dumps({
                "status": "infeasible",
                "message": "No valid schedule exists with current constraints",
                "conflicts": conflicts if conflicts else ["Unable to determine specific conflicts"],
                "suggestions": [
                    "Add more rooms or increase room capacities",
                    "Reduce number of sessions or session durations",
                    "Extend event duration (later end time or earlier start)",
                    "Split sessions across multiple days",
                    "Consider parallel tracks in different rooms",
                    "Remove or reduce lunch break duration",
                    "Reduce travel time requirements for speakers"
                ]
            }, indent=2)
        
        else:
            return json.dumps({
                "status": "unknown",
                "message": f"Solver returned status: {solver.StatusName(status)}",
                "suggestion": "Try adjusting constraints or increasing time limit"
            }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Scheduling optimization failed: {str(e)}",
            "details": "Check input format and try again"
        }, indent=2)


@function_tool
def analyze_schedule_conflicts(
    current_schedule: str,
    new_session: str
) -> str:
    """
    Analyze if adding a new session would cause conflicts.
    
    Args:
        current_schedule: JSON string of existing schedule
        new_session: JSON string of new session to add
    
    Returns:
        JSON string with conflict analysis
    """
    try:
        schedule = json.loads(current_schedule) if isinstance(current_schedule, str) else current_schedule
        session = json.loads(new_session) if isinstance(new_session, str) else new_session
        
        conflicts = []
        suggestions = []
        
        # Check time overlaps
        new_start = parse_time_to_minutes(session.get('start_time', '09:00'))
        new_end = new_start + session.get('duration', 60)
        
        for existing in schedule:
            ex_start = parse_time_to_minutes(existing.get('start_time', '09:00'))
            ex_end = parse_time_to_minutes(existing.get('end_time', '10:00'))
            
            # Check room conflict
            if session.get('room') == existing.get('room'):
                if not (new_end <= ex_start or new_start >= ex_end):
                    conflicts.append({
                        "type": "room_conflict",
                        "message": f"Room '{session.get('room')}' is occupied by '{existing.get('session_name')}' from {existing.get('start_time')}-{existing.get('end_time')}",
                        "severity": "high"
                    })
                    suggestions.append(f"Move to different room or reschedule to before {existing.get('start_time')} or after {existing.get('end_time')}")
            
            # Check speaker conflict
            if session.get('speaker') == existing.get('speaker'):
                if not (new_end <= ex_start or new_start >= ex_end):
                    conflicts.append({
                        "type": "speaker_conflict",
                        "message": f"Speaker '{session.get('speaker')}' is already scheduled for '{existing.get('session_name')}' at {existing.get('start_time')}",
                        "severity": "critical"
                    })
                    suggestions.append(f"Find different speaker or reschedule session")
        
        if not conflicts:
            return json.dumps({
                "status": "no_conflicts",
                "message": "New session can be added without conflicts",
                "recommended_action": "Proceed with adding session"
            }, indent=2)
        else:
            return json.dumps({
                "status": "conflicts_detected",
                "conflicts": conflicts,
                "suggestions": suggestions,
                "recommended_action": "Resolve conflicts before adding session"
            }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Conflict analysis failed: {str(e)}"
        }, indent=2)


def create_scheduling_agent() -> Agent:
    """Create advanced scheduling agent with constraint optimization capabilities."""
    return Agent(
        name="Advanced Scheduling Specialist",
        handoff_description="Optimizes complex event schedules using constraint programming to resolve conflicts and maximize efficiency.",
        instructions="Schedule optimizer using OR-Tools. Use optimize_schedule() to resolve conflicts and create optimal schedules. Input: sessions, rooms, speakers, constraints. Return JSON with schedule, metrics, or conflict explanations.",
        tools=[optimize_schedule, analyze_schedule_conflicts]
    )
