"""High level workflow entrypoint for event planning.

Intelligent 3-phase workflow:
1. Coordinator analyzes event and decides which agents to use + order
2. Run those agents and collect outputs
3. Coordinator reviews, refines, and finalizes (can call new agents if needed)

Design:
- Coordinator makes strategic decisions (which agents, what order, what refinements)
- Specialists do domain-specific work
- Coordinator can iterate and call additional agents as needed
"""
from typing import Dict, Any, List
import json
import datetime
import asyncio
import shutil
import os
import logging
from pathlib import Path

# Import from extracted modules
from workflows.schemas import AGENT_SCHEMAS, validate_agent_output
from workflows.prompts import (
    build_planning_prompt,
    build_specialist_prompt,
    build_finalization_prompt,
    build_calendar_prompt,
    build_form_prompt,
    build_logo_prompt,
)
from workflows.mcp_setup import (
    setup_sandboxed_local_tally_mcp,
    setup_unsandboxed_tally_mcp,
    setup_sandboxed_filesystem_mcp,
)
from workflows.workflow_utils import (
    get_current_date_context,
    copy_sandbox_files_to_project,
    create_basic_schedule,
    run_sync_with_backoff,
)

# Allow longer agent exchanges (default 10 can be too short for tool-rich agents)
AGENT_MAX_TURNS = 20

# Sandboxed MCP configuration
SANDBOX_DIR = Path("/tmp/mcp_event_outputs")
PROJECT_OUTPUT_DIR = Path(__file__).parent.parent / "event_outputs"
SANDBOX_ENABLED = True  # Set to False to disable sandboxing
USE_SANDBOXED_FORMS = None  # Will be set by user preference
SKIP_FORM_CREATION = False  # Allows headless runs to bypass form generation

# Global references to keep MCP servers alive (prevent premature garbage collection)
_fs_server_ref = None
_tally_server_ref = None

# Setup file logging
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def setup_workflow_logger():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"workflow_{timestamp}.log"
    logger = logging.getLogger(f"workflow_{timestamp}")  # Unique logger per run
    logger.setLevel(logging.DEBUG)
    logger.handlers = []  # Clear existing handlers
    logger.propagate = False  # Don't propagate to root logger
    fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger, log_file





def run_event_planning(event_details: Dict[str, Any], progress_tracker: Dict[str, Any] = None) -> Dict[str, Any]:
    """Intelligent multi-phase workflow with coordinator orchestration.

    Phase 1: Coordinator Planning
    - Analyzes event requirements
    - Decides which specialists are needed
    - Determines optimal order of execution

    Phase 2: Specialist Execution
    - Calls each specialist in the determined order
    - Collects all outputs

    Phase 3: Coordinator Finalization
    - Reviews all specialist outputs
    - Identifies gaps, conflicts, or issues
    - Calls additional agents if needed
    - Produces final unified plan
    """
    # Setup logging
    logger, log_file = setup_workflow_logger()
    logger.info("="*80)
    logger.info("Starting Event Planning Workflow")
    logger.info(f"Event: {event_details.get('event_name', 'Unknown')}")
    logger.info(f"Log file: {log_file}")
    logger.info("="*80)
    
    def update_progress(phase, phase_name, status, agents=None, current_agent=None, message=""):
        """Update progress tracker for real-time frontend updates."""
        if progress_tracker is not None:
            progress_tracker["phase"] = phase
            progress_tracker["phase_name"] = phase_name
            progress_tracker["status"] = status
            if agents is not None:
                progress_tracker["agents"] = agents
            progress_tracker["current_agent"] = current_agent
            progress_tracker["message"] = message
    
    # Ensure an asyncio event loop exists for sync runner on Python 3.13+
    # Create ONE loop and use it throughout the workflow
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Import SDK components
    try:
        from agents import Runner
        from custom_agents.base import create_specialized_agents
        from custom_agents.coordinator_agent import create_coordinator_agent
    except Exception as exc:
        raise RuntimeError(f"Required imports failed: {exc}")

    print(f"\n{'='*60}")
    print(f"🎉 AI EVENT PLANNER")
    print(f"{'='*60}")
    print(f"Event: {event_details['event_name']}")
    print(f"Type: {event_details['event_type']}")
    print(f"Date Context: {get_current_date_context()}")
    print(f"{'='*60}\n")
    
    # Ask user preference for form creation method (only in interactive mode)
    global USE_SANDBOXED_FORMS
    # Skip prompt if already set or running non-interactively
    is_non_interactive = os.environ.get("EVENT_PLANNER_NON_INTERACTIVE") == "1"
    
    # Check if dev settings override is provided
    if is_non_interactive and os.environ.get("EVENT_PLANNER_ENABLE_SANDBOX"):
        USE_SANDBOXED_FORMS = os.environ.get("EVENT_PLANNER_ENABLE_SANDBOX") == "1"
        mode_text = "sandboxed (Docker)" if USE_SANDBOXED_FORMS else "unsandboxed (mcp-remote)"
        print(f"\n✅ Dev settings: Using {mode_text} for forms\n")
    elif USE_SANDBOXED_FORMS is None and not is_non_interactive:
        try:
            print("\n📋 FORM CREATION METHOD SELECTION")
            print("-" * 60)
            print("How would you like to create registration forms?\n")
            print("1. Sandboxed (Recommended) - Custom local MCP in Docker sandbox")
            print("   ✅ Runs in isolated container")
            print("   ✅ Network-restricted (api.tally.so only)")
            print("   ✅ Uses Tally REST API directly\n")
            print("2. Unsandboxed - Official Tally mcp-remote server")
            print("   ⚠️  No sandboxing (direct system access)")
            print("   ⚠️  OAuth2 authentication (may have issues)")
            print("   ⚠️  External npm package dependency\n")
            
            while True:
                choice = input("Enter your choice (1 or 2): ").strip()
                if choice == "1":
                    USE_SANDBOXED_FORMS = True
                    print("\n✅ Using sandboxed local MCP server for forms\n")
                    break
                elif choice == "2":
                    USE_SANDBOXED_FORMS = False
                    print("\n✅ Using unsandboxed Tally mcp-remote for forms\n")
                    break
                else:
                    print("⚠️  Invalid choice. Please enter 1 or 2.\n")
        except (EOFError, OSError):
            # Non-interactive mode (e.g., API call) - use default
            USE_SANDBOXED_FORMS = False
            print("\n✅ Non-interactive mode: Using unsandboxed Tally mcp-remote for forms\n")

    # ============================================================
    # PHASE 1: COORDINATOR PLANNING
    # ============================================================
    print("📋 PHASE 1: Strategic Planning\n")
    print("Coordinator analyzing event requirements...\n")

    # Install custom asyncio exception handler to suppress MCP cleanup errors
    # (Python 3.13 + MCP library compatibility issue - cosmetic only)
    def suppress_mcp_cleanup_errors(loop_arg, context):
        """Suppress asyncio cleanup errors from MCP async generators."""
        exception = context.get('exception')
        message = context.get('message', '')
        
        # DEBUG: Log what we're seeing
        if exception:
            print(f"DEBUG: Exception handler caught: {type(exception).__name__}: {exception}")
        
        if exception and isinstance(exception, RuntimeError):
            if 'cancel scope' in str(exception).lower():
                # This is the expected MCP cleanup error - silently ignore
                print("DEBUG: Suppressing cancel scope error")
                return
        # For other errors, use default handler
        print("DEBUG: Using default handler for exception")
        loop_arg.default_exception_handler(context)
    
    # Install the handler on the existing event loop
    loop.set_exception_handler(suppress_mcp_cleanup_errors)

    # Setup sandboxed MCP servers based on user preferences
    # Keep global references to prevent premature garbage collection
    # NOTE: Filesystem MCP setup is DELAYED until Phase 4 (calendar creation)
    # to avoid connection closing during Phase 2-3 specialist agent execution
    global SANDBOX_ENABLED, _fs_server_ref, _tally_server_ref
    fs_server = None  # Will be set up in Phase 4
    tally_server = None
    _fs_server_ref = None
    _tally_server_ref = None
    
    # Setup Tally MCP based on user preference
    if USE_SANDBOXED_FORMS:
        try:
            print("🔒 Setting up sandboxed local Tally MCP server...\n")
            custom_mcp_dir = Path(__file__).parent.parent / "custom_mcp_servers"
            tally_server = loop.run_until_complete(setup_sandboxed_local_tally_mcp(custom_mcp_dir))
            _tally_server_ref = tally_server  # Keep global reference to prevent GC
            print("✅ Custom Tally MCP initialized - forms will be sandboxed\n")
        except Exception as e:
            print(f"⚠️  Sandboxed Tally MCP setup failed: {e}\n")
            print("⏸️  Forms will not be created\n")
            tally_server = None
            _tally_server_ref = None
    else:
        # For unsandboxed path, let form_agent manage the official mcp-remote client itself.
        print("📡 Using unsandboxed Tally mcp-remote (managed inside form_agent)...\n")
        tally_server = None
        _tally_server_ref = None

    # Create all available specialists (coordinator will decide which to use)
    # Note: calendar form and Logo are NOT in this list because they're Phase 4 output generators,
    # not Phase 2 domain specialists. They're created separately below after Phase 2 execution.
    all_agent_types = [
        "venue", "catering", "programme", "speakers", 
        "communication", "activities", "entertainment", "budgeting", "scheduling"
    ]
    all_specialists = create_specialized_agents(all_agent_types, mcp_servers=None)  # Phase 2 specialists don't need MCP
    
    # Status summary
    # Note: Calendar MCP is set up later in Phase 4 (right before use) to prevent connection closing
    calendar_status = "sandboxed" if SANDBOX_ENABLED else "local I/O"
    if USE_SANDBOXED_FORMS:
        form_status = "sandboxed (custom)" if tally_server else "disabled"
    else:
        # Unsandboxed path is handled internally by form_agent via mcp-remote
        form_status = "unsandboxed (mcp-remote via form_agent)"
    print(f"📊 Output Configuration: Calendar={calendar_status}, Forms={form_status}\n")
    
    # Create coordinator with handoffs to all specialists
    coordinator = create_coordinator_agent(event_details, all_agent_types, all_specialists)

    planning_prompt = build_planning_prompt(event_details)
    planning_result = run_sync_with_backoff(coordinator, planning_prompt, max_turns=AGENT_MAX_TURNS)
    
    # Parse the planning decision
    try:
        planning_data = json.loads(planning_result.final_output)
        required_agents = planning_data.get("required_agents", all_agent_types[:6])
        print(f"✅ Planning complete!")
        print(f"\n� Selected agents (in order): {', '.join(required_agents)}")
        print(f"💡 Rationale: {planning_data.get('execution_order_rationale', 'N/A')}\n")
    except:
        # Fallback if parsing fails
        required_agents = all_agent_types[:6]
        print(f"⚠️  Using default agent selection\n")

    # ============================================================
    # PHASE 2: SPECIALIST EXECUTION
    # ============================================================
    print(f"\n{'='*60}")
    print("🔧 PHASE 2: Specialist Execution")
    print(f"{'='*60}\n")
    
    update_progress("phase_2", "Agents Working", "in_progress", agents=required_agents, message="Starting specialist execution...")
    
    specialist_outputs = {}
    # Initialize agent status tracking
    agent_statuses = []
    for agent_name in required_agents:
        agent_statuses.append({"name": agent_name, "status": "pending"})
    
    for idx, agent_name in enumerate(required_agents, 1):
        if agent_name not in all_specialists:
            print(f"⚠️  Skipping unknown agent: {agent_name}")
            continue
            
        # Update status to working
        for agent_stat in agent_statuses:
            if agent_stat["name"] == agent_name:
                agent_stat["status"] = "working"
        
        # Update progress tracker
        update_progress("phase_2", "Agents Working", "in_progress", 
                       agents=agent_statuses.copy(), 
                       current_agent=agent_name,
                       message=f"Running {agent_name} specialist...")
        
        agent = all_specialists[agent_name]
        
        print(f"[{idx}/{len(required_agents)}] 🎯 {agent_name.title()} Specialist")
        print(f"{'─'*40}")
        
        # Build context-aware prompt with prior outputs
        context = ""
        if specialist_outputs:
            context = f"\n\nPrevious specialist outputs for context:\n{json.dumps(specialist_outputs, indent=2)}"
        
        specialist_prompt = build_specialist_prompt(
            agent_name=agent_name,
            event_details=event_details,
            context=context,
            specialist_outputs=specialist_outputs,
            required_agents=required_agents
        )
        result = Runner.run_sync(agent, specialist_prompt, max_turns=AGENT_MAX_TURNS)
        
        # Log raw agent output for debugging
        print(f"   📄 Raw agent output ({len(result.final_output)} chars): {result.final_output[:300]}...")
        logger.info(f"Agent '{agent_name}' output length: {len(result.final_output)} chars")
        logger.debug(f"Agent '{agent_name}' full output: {result.final_output}")
        
        # Validate and normalize output to match schema
        try:
            validated_output = validate_agent_output(agent_name, result.final_output)
            specialist_outputs[agent_name] = validated_output
            print(f"   ✅ Output validated successfully")
            logger.info(f"Agent '{agent_name}' validation: SUCCESS")
        except ValueError as e:
            print(f"⚠️  Schema validation error for {agent_name}: {e}")
            logger.warning(f"Agent '{agent_name}' validation FAILED: {e}")
            print(f"   Attempting to parse JSON anyway...")
            
            # Try to parse JSON even if validation fails
            try:
                import re
                output_str = result.final_output.strip()
                
                # Try multiple JSON extraction strategies
                parsed = None
                
                # Strategy 1: Try direct JSON parse
                try:
                    parsed = json.loads(output_str)
                except json.JSONDecodeError:
                    pass
                
                # Strategy 2: Extract JSON from code blocks
                if not parsed:
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', output_str, re.DOTALL)
                    if json_match:
                        try:
                            parsed = json.loads(json_match.group(1))
                        except json.JSONDecodeError:
                            pass
                
                # Strategy 3: Find JSON object in text
                if not parsed:
                    json_match = re.search(r'\{[^{}]*(?:"summary"|"venues"|"name")[^{}]*\}', output_str, re.DOTALL)
                    if json_match:
                        try:
                            # Try to fix common JSON issues
                            json_str = json_match.group(0)
                            # Remove trailing commas before closing braces/brackets
                            json_str = re.sub(r',\s*}', '}', json_str)
                            json_str = re.sub(r',\s*]', ']', json_str)
                            parsed = json.loads(json_str)
                        except json.JSONDecodeError:
                            pass
                
                if parsed and isinstance(parsed, dict):
                    print(f"   ✅ Successfully parsed JSON despite validation error")
                    specialist_outputs[agent_name] = parsed
                    logger.info(f"Agent '{agent_name}' parsed JSON successfully despite validation error")
                else:
                    print(f"   ⚠️  Could not parse JSON, storing raw output...")
                    specialist_outputs[agent_name] = result.final_output
            except Exception as parse_ex:
                print(f"   ⚠️  JSON parsing failed: {parse_ex}, storing raw output...")
                specialist_outputs[agent_name] = result.final_output
        
        # Update status to done
        for agent_stat in agent_statuses:
            if agent_stat["name"] == agent_name:
                agent_stat["status"] = "done"
        
        # Update progress tracker
        update_progress("phase_2", "Agents Working", "in_progress", 
                       agents=agent_statuses.copy(),
                       message=f"Completed {agent_name} specialist")
        
        print(f"✓ Complete\n")

    # ============================================================
    # PHASE 3: COORDINATOR FINALIZATION
    # ============================================================
    print(f"\n{'='*60}")
    print("🎯 PHASE 3: Review, Refinement & Finalization")
    print(f"{'='*60}\n")
    
    update_progress("phase_3", "Coordinator Finalizing", "in_progress", message="Reviewing and refining outputs...")
    
    print("Coordinator reviewing all outputs...\n")

    finalization_prompt = build_finalization_prompt(
        event_details=event_details,
        required_agents=required_agents,
        specialist_outputs=specialist_outputs
    )
    final_result = run_sync_with_backoff(coordinator, finalization_prompt, max_turns=AGENT_MAX_TURNS)
    
    print("✅ Finalization complete!\n")
    
    # ============================================================
    # PHASE 4: Event Outputs (CALENDAR & REGISTRATION FORM)
    # ============================================================
    print(f"\n{'='*60}")
    print("📅 PHASE 4: Event Outputs (Calendar & Registration Form)")
    print(f"{'='*60}\n")
    
    update_progress("phase_4", "Generating Outputs", "in_progress", message="Creating calendar and registration form...")
    
    # Auto-approve sandbox confirmations in non-interactive mode
    is_non_interactive = os.environ.get("EVENT_PLANNER_NON_INTERACTIVE") == "1"
    original_input = None
    if is_non_interactive:
        import builtins
        original_input = builtins.input
        def _auto_approve_input(prompt: str = "") -> str:
            # Auto-approve any sandbox confirmation prompts
            if any(keyword in prompt.lower() for keyword in ["approve", "confirm", "allow", "yes", "y/n"]):
                print(f"Auto-approving: {prompt.strip()}")
                return "y" if "y/n" in prompt.lower() else "yes"
            # Default response for any other prompts
            return "yes"
        builtins.input = _auto_approve_input
    
    # Setup filesystem MCP NOW (right before calendar creation) to prevent connection closing
    # This avoids the ClosedResourceError that happens when MCP is set up earlier
    if SANDBOX_ENABLED and fs_server is None:
        try:
            print("🔒 Setting up sandboxed filesystem server...\n")
            # Create fresh event loop for MCP setup (matches test pattern)
            mcp_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(mcp_loop)
            fs_server = mcp_loop.run_until_complete(setup_sandboxed_filesystem_mcp(SANDBOX_DIR, PROJECT_OUTPUT_DIR))
            _fs_server_ref = fs_server  # Keep global reference to prevent GC
            # Don't close the loop - keep it alive for calendar agent
            loop = mcp_loop  # Update loop reference to use the same one
            print("✅ Filesystem MCP initialized - calendar will be sandboxed\n")
        except Exception as e:
            print(f"⚠️  Filesystem MCP setup failed: {e}\n")
            print("⏸️  Falling back to local I/O for calendar\n")
            fs_server = None
            _fs_server_ref = None
    
    # Create calendar, form, and logo agents now (not part of Phase 2 coordinator selection)
    from custom_agents.calendar_agent import create_calendar_agent
    from custom_agents.form_agent import create_form_agent
    from custom_agents.logo_agent import create_logo_agent
    
    # Calendar agent: use sandboxed filesystem MCP (if available)
    print(f"DEBUG: fs_server = {fs_server}, type = {type(fs_server)}\n")
    calendar_agent = create_calendar_agent(mcp_servers=fs_server if fs_server else None)
    
    # Form agent:
    # - sandboxed path: pass the custom MCP server
    # - unsandboxed path: pass None so form_agent uses mcp-remote internally
    form_agent = create_form_agent(mcp_servers=tally_server if USE_SANDBOXED_FORMS else None)
    
    # Add calendar, form, and logo agents to status tracking
    agent_statuses.append({"name": "calendar", "status": "pending"})
    agent_statuses.append({"name": "form", "status": "pending"})
    agent_statuses.append({"name": "logo", "status": "pending"})
    update_progress("phase_4", "Generating Outputs", "in_progress", 
                   agents=agent_statuses.copy(),
                   current_agent="calendar",
                   message="Creating calendar invite...")
    
    # Create calendar invite
    print("Creating calendar invite file...\n")
    
    # Update calendar agent status
    for agent_stat in agent_statuses:
        if agent_stat["name"] == "calendar":
            agent_stat["status"] = "working"
    update_progress("phase_4", "Generating Outputs", "in_progress", 
                   agents=agent_statuses.copy(),
                   current_agent="calendar",
                   message="Generating calendar file...")
    
    calendar_prompt = build_calendar_prompt(
        event_details=event_details,
        specialist_outputs=specialist_outputs,
        final_result_output=final_result.final_output
    )

    calendar_result = None
    try:
        # Runner.run_sync will use the current event loop (which is mcp_loop if MCP is enabled)
        # This works because we called asyncio.set_event_loop(mcp_loop) during MCP setup
        calendar_result = Runner.run_sync(calendar_agent, calendar_prompt, max_turns=AGENT_MAX_TURNS)
        print("✅ Calendar invite generated!\n")
        
        # Update calendar agent status
        for agent_stat in agent_statuses:
            if agent_stat["name"] == "calendar":
                agent_stat["status"] = "done"
        update_progress("phase_4", "Generating Outputs", "in_progress", 
                       agents=agent_statuses.copy(),
                       current_agent="form",
                       message="Calendar created successfully")
    except RuntimeError as rt_ex:
        # Handle asyncio cleanup errors (Python 3.13 stricter checks)
        # The agent completes successfully, but cleanup throws an error during async generator teardown
        if "cancel scope" in str(rt_ex).lower():
            print("⚠️  AsyncIO cleanup warning detected (non-breaking)\n")
            # Check if calendar file was actually created despite the error
            import glob
            calendar_files = glob.glob("event_outputs/*.ics")
            if calendar_files:
                print(f"✅ Calendar file created successfully: {calendar_files[-1]}\n")
                # Create result object from the actual file
                calendar_result = type('obj', (object,), {
                    'final_output': json.dumps({
                        "calendar_file_path": calendar_files[-1],
                        "event_summary": "Calendar created successfully",
                        "timing_details": "See calendar file in event_outputs/",
                        "import_instructions": "Import the .ics file to your calendar app"
                    })
                })()
            else:
                print("❌ Calendar file not found despite cleanup warning\n")
                raise
        else:
            raise
    except Exception as cal_ex:
        import traceback
        print(f"⚠️  Calendar generation failed: {type(cal_ex).__name__}: {cal_ex}\n")
        print(f"   Full traceback:\n")
        traceback.print_exc()
        print(f"\n   Continuing workflow without calendar...\n")
        # Create a minimal calendar result to prevent downstream errors
        calendar_result = type('obj', (object,), {
            'final_output': json.dumps({
                "calendar_file_path": "Error",
                "event_summary": "Calendar generation failed",
                "timing_details": str(cal_ex),
                "import_instructions": "Calendar could not be generated"
            })
        })()
        # Update calendar agent status even on error
        for agent_stat in agent_statuses:
            if agent_stat["name"] == "calendar":
                agent_stat["status"] = "done"
        update_progress("phase_4", "Generating Outputs", "in_progress", 
                       agents=agent_statuses.copy(),
                       current_agent="form",
                       message="Calendar generation completed (with errors)")
    
    # Create registration form
    if SKIP_FORM_CREATION:
        print("⏭️  Skipping registration form creation (headless mode)\n")
        form_data = {"status": "skipped", "form_url": None, "message": "Form creation skipped"}
        # Update form agent status
        for agent_stat in agent_statuses:
            if agent_stat["name"] == "form":
                agent_stat["status"] = "done"
    else:
        # Update form agent status
        for agent_stat in agent_statuses:
            if agent_stat["name"] == "form":
                agent_stat["status"] = "working"
        update_progress("phase_4", "Generating Outputs", "in_progress", 
                       agents=agent_statuses.copy(),
                       current_agent="form",
                       message="Creating registration form...")
        
        print("Creating event registration form...\n")
        
        # Compact prompt to reduce tokens: only essentials
        concise_event = {
            "event_name": event_details.get("event_name"),
            "event_type": event_details.get("event_type"),
            "event_date": event_details.get("event_date"),
            "location": event_details.get("location_preference"),
            "guest_count": event_details.get("guest_count"),
            "special_requirements": event_details.get("special_requirements"),
        }
        # Derive any minimal context from specialists without full dumps
        minimal_context = {}
        if "venue" in specialist_outputs:
            minimal_context["venue"] = "include venue/address field if available"
        if "catering" in specialist_outputs:
            minimal_context["catering"] = "collect dietary restrictions"
        # Registration form will be auto-generated in Phase 4
        if "programme" in specialist_outputs:
            minimal_context["programme"] = "optional session preferences"

        form_prompt = build_form_prompt(
            event_details=event_details,
            concise_event=concise_event,
            minimal_context=minimal_context
        )

        # Create the form via shared helper (handles retries/backoff)
        # Pass sandboxed Tally server if enabled
        try:
            from custom_agents.form_agent import extract_form_url_from_output, run_form_with_retries

            form_result, form_error = run_form_with_retries(form_prompt, mcp_servers=tally_server if SANDBOX_ENABLED else None)

            # Extract form URL from output; on failure, surface the error instead of generating a local fallback
            form_data = extract_form_url_from_output(form_result.final_output if form_result else "")

            # Check if we have a URL (even if status extraction failed)
            form_url = form_data.get("form_url", "")
            has_url = bool(form_url and form_url.startswith("http"))
            
            if has_url or form_data.get("status") == "success":
                if has_url:
                    print(f"✅ Registration form created: {form_url}\n")
                else:
                    print(f"✅ Registration form created (URL extraction had issues)\n")
                # Update form agent status
                for agent_stat in agent_statuses:
                    if agent_stat["name"] == "form":
                        agent_stat["status"] = "done"
                update_progress("phase_4", "Generating Outputs", "in_progress", 
                               agents=agent_statuses.copy(),
                               current_agent=None,
                               message="Registration form created successfully")
                # Ensure form_data has the URL
                if has_url:
                    form_data["status"] = "success"
                    form_data["form_url"] = form_url
            else:
                # Extract error message - check if form_error is actually an error or just a message
                error_message = form_data.get("message") or "Unknown error during form creation"
                
                # Don't show form_error if it's a success message
                if form_error and "error" in form_error.lower() and "success" not in form_error.lower():
                    error_message = form_error
                elif form_error and "created successfully" in form_error.lower():
                    # The agent said it was created but we couldn't extract the URL
                    error_message = "Form may have been created, but URL could not be extracted. " + form_data.get("message", "")
                
                print(f"⚠️  Form creation failed. Error: {error_message}\n")
                if form_data.get("raw_output"):
                    print(f"   Raw output preview: {form_data.get('raw_output')[:200]}...\n")
                form_data = {
                    "status": "error",
                    "message": error_message,
                    "raw_output": form_data.get("raw_output")
                }
                # Update form agent status
                for agent_stat in agent_statuses:
                    if agent_stat["name"] == "form":
                        agent_stat["status"] = "done"
                update_progress("phase_4", "Generating Outputs", "in_progress", 
                               agents=agent_statuses.copy(),
                               current_agent=None,
                               message="Form creation completed (with errors)")
        except RuntimeError as rt_ex:
            # Ignore asyncio cleanup errors (Python 3.13 stricter checks)
            if "cancel scope" in str(rt_ex):
                print(f"⚠️  Form creation had asyncio cleanup warning (non-fatal)\n")
                print(f"   Continuing workflow...\n")
                form_data = {
                    "status": "error",
                    "message": "Form creation completed but had cleanup issues"
                }
            else:
                print(f"⚠️  Form creation exception: {rt_ex}\n")
                print(f"   Continuing workflow without form...\n")
                form_data = {
                    "status": "error",
                    "message": f"Form creation failed: {str(rt_ex)}"
                }
            # Update form agent status
            for agent_stat in agent_statuses:
                if agent_stat["name"] == "form":
                    agent_stat["status"] = "done"
            update_progress("phase_4", "Generating Outputs", "in_progress", 
                           agents=agent_statuses.copy(),
                           current_agent=None,
                           message="Form creation completed (with cleanup issues)")
        except Exception as form_ex:
            print(f"⚠️  Form creation exception: {form_ex}\n")
            print(f"   Continuing workflow without form...\n")
            form_data = {
                "status": "error",
                "message": f"Form creation failed: {str(form_ex)}"
            }
            # Update form agent status
            for agent_stat in agent_statuses:
                if agent_stat["name"] == "form":
                    agent_stat["status"] = "done"
            update_progress("phase_4", "Generating Outputs", "in_progress", 
                           agents=agent_statuses.copy(),
                           current_agent=None,
                           message="Form creation failed")
    
    # Create logo
    logo_agent = create_logo_agent()
    
    # Update logo agent status
    for agent_stat in agent_statuses:
        if agent_stat["name"] == "logo":
            agent_stat["status"] = "working"
    update_progress("phase_4", "Generating Outputs", "in_progress", 
                   agents=agent_statuses.copy(),
                   current_agent="logo",
                   message="Generating logo...")
    
    print("Creating event logo...\n")
    
    logo_prompt = build_logo_prompt(
        event_details=event_details,
        specialist_outputs=specialist_outputs,
        final_result_output=final_result.final_output
    )

    logo_result = None
    logo_data = {}
    try:
        logo_result = Runner.run_sync(logo_agent, logo_prompt, max_turns=AGENT_MAX_TURNS)
        print("✅ Logo generated!\n")
        
        # Parse logo output
        try:
            logo_data = json.loads(logo_result.final_output)
            if logo_data.get("status") == "success":
                print(f"✅ Logo file created: {logo_data.get('logo_file_path')}\n")
            else:
                print(f"⚠️  Logo generation returned error status\n")
        except json.JSONDecodeError:
            # Try to extract JSON from markdown if present
            output_str = logo_result.final_output
            if '```json' in output_str:
                json_str = output_str.split('```json')[1].split('```')[0].strip()
                logo_data = json.loads(json_str)
            else:
                # Try to find JSON object in the output
                import re
                match = re.search(r'\{.*\}', output_str, re.DOTALL)
                if match:
                    logo_data = json.loads(match.group())
                else:
                    logo_data = {"status": "error", "message": "Could not parse logo output"}
        
        # Update logo agent status
        for agent_stat in agent_statuses:
            if agent_stat["name"] == "logo":
                agent_stat["status"] = "done"
        update_progress("phase_4", "Generating Outputs", "in_progress", 
                       agents=agent_statuses.copy(),
                       current_agent=None,
                       message="Logo generated successfully")
    except Exception as logo_ex:
        import traceback
        print(f"⚠️  Logo generation failed: {type(logo_ex).__name__}: {logo_ex}\n")
        print(f"   Full traceback:\n")
        traceback.print_exc()
        print(f"\n   Continuing workflow without logo...\n")
        logo_data = {
            "status": "error",
            "message": f"Logo generation failed: {str(logo_ex)}"
        }
        # Update logo agent status even on error
        for agent_stat in agent_statuses:
            if agent_stat["name"] == "logo":
                agent_stat["status"] = "done"
        update_progress("phase_4", "Generating Outputs", "in_progress", 
                       agents=agent_statuses.copy(),
                       current_agent=None,
                       message="Logo generation completed (with errors)")
    
    # Final update for Phase 4 completion
    update_progress("phase_4", "Generating Outputs", "completed", 
                   agents=agent_statuses.copy(),
                   current_agent=None,
                   message="Calendar, registration form, and logo completed")
    
    # ============================================================
    # PHASE 5: PDF REPORT GENERATION
    # ============================================================
    print(f"\n{'='*60}")
    print("📄 PHASE 5: Generating Professional PDF Report")
    print(f"{'='*60}\n")
    
    update_progress("phase_5", "Generating Report", "in_progress", message="Creating comprehensive PDF proposal...")
    
    try:
        from tools.report_generator import generate_event_proposal_pdf
        
        # Validate final plan against schema (this enforces timeline field and recommendations)
        try:
            final_plan_dict = validate_agent_output("final_plan", final_result.final_output, required_agents=required_agents)
            print(f"✅ Final plan validated successfully (includes timeline: {bool(final_plan_dict.get('timeline'))}, recommendations: {bool(final_plan_dict.get('recommendations'))})")
        except ValueError as e:
            print(f"⚠️  Final plan schema validation error: {e}")
            print(f"   This means the coordinator did not generate all required fields (including timeline)")
            print(f"   Attempting to parse and add missing fields...")
            # Try to parse anyway
            parsed = final_result.final_output
            if isinstance(parsed, str):
                try:
                    parsed = json.loads(parsed)
                except:
                    try:
                        if '```json' in parsed:
                            json_str = parsed.split('```json')[1].split('```')[0].strip()
                        elif '```' in parsed:
                            json_str = parsed.split('```')[1].split('```')[0].strip()
                        else:
                            import re
                            match = re.search(r'\{.*\}', parsed, re.DOTALL)
                            if match:
                                json_str = match.group(0)
                            else:
                                raise ValueError("No JSON found")
                        parsed = json.loads(json_str)
                    except:
                        parsed = {}
            
            if not isinstance(parsed, dict):
                parsed = {}
            
            # Ensure all required schema fields exist (add empty defaults if missing)
            schema = AGENT_SCHEMAS.get("final_plan", {})
            for key in schema.keys():
                if key not in parsed:
                    print(f"   Adding missing field: {key}")
                    if key == "timeline":
                        parsed[key] = []
                    elif key == "schedule":
                        # Create a basic schedule from event details if none exists
                        basic_schedule = create_basic_schedule(event_details)
                        parsed[key] = basic_schedule
                        print(f"   Created basic schedule with {len(basic_schedule.get('sessions', []))} sessions")
                    elif key == "budget":
                        parsed[key] = {"total_available": 0, "total_allocated": 0, "by_category": {}, "status": "unknown"}
                    elif key == "recommendations":
                        parsed[key] = {}
                    elif key == "risks":
                        parsed[key] = []
                    elif key == "action_items":
                        parsed[key] = []
                    elif key == "assumptions":
                        parsed[key] = []
                    else:
                        parsed[key] = ""
            
            # Ensure schedule always has at least one session
            if "schedule" in parsed:
                schedule = parsed["schedule"]
                if not isinstance(schedule, dict):
                    schedule = {"optimized": False, "sessions": []}
                    parsed["schedule"] = schedule
                
                if "sessions" not in schedule or not schedule.get("sessions"):
                    # Create basic schedule if sessions are missing or empty
                    basic_schedule = create_basic_schedule(event_details)
                    parsed["schedule"] = basic_schedule
                    print(f"   Schedule was empty, created basic schedule with {len(basic_schedule.get('sessions', []))} sessions")
            
            final_plan_dict = parsed
        
        pdf_path = generate_event_proposal_pdf(
            event_details=event_details,
            final_plan=final_plan_dict,
            specialist_outputs=specialist_outputs
        )
        
        print(f"✅ PDF report generated: {pdf_path}\n")
        pdf_generated = True
        
    except Exception as e:
        print(f"⚠️  PDF generation error: {e}\n")
        pdf_path = None
        pdf_generated = False
    
    # ============================================================
    # PHASE 6: SMS NOTIFICATION (OPTIONAL)
    # ============================================================
    print(f"\n{'='*60}")
    print("📱 PHASE 6: SMS Notification")
    print(f"{'='*60}\n")
    
    # Ask user if they want to send SMS (skip in non-interactive mode)
    is_non_interactive = os.environ.get("EVENT_PLANNER_NON_INTERACTIVE") == "1"
    
    if is_non_interactive:
        # Check dev settings override
        enable_sms = os.environ.get("EVENT_PLANNER_ENABLE_SMS") == "1"
        send_sms = 'yes' if enable_sms else 'no'
        status = "enabled" if enable_sms else "disabled"
        print(f"✅ Dev settings: SMS notification {status}\n")
    else:
        try:
            send_sms = input("Do you want to send event details via SMS (costs 1$ per sms and we only have 7$ left so please use responsiibily)? (yes/no): ").lower().strip()
        except (EOFError, OSError):
            # Non-interactive mode - skip SMS by default
            send_sms = 'no'
            print("✅ Non-interactive mode: Skipping SMS notification\n")
        
    try:
        if send_sms in ['yes', 'y', 'true', '1']:
            print("Sending SMS notification...\n")
            
            try:
                from tools.sms_notifier import send_event_sms
                
                # Send SMS using the SMS notifier tool
                form_url = form_data.get('form_url')
                sms_result = send_event_sms(
                    event_details=event_details,
                    form_url=form_url
                )
                
                if sms_result.get('success'):
                    print(f"✅ SMS sent successfully! Message SID: {sms_result.get('message_sid')}\n")
                    sms_sent = True
                    sms_message_sid = sms_result.get('message_sid')
                else:
                    error_msg = sms_result.get('error', 'Unknown error')
                    print(f"⚠️  Failed to send SMS: {error_msg}\n")
                    sms_sent = False
                    sms_message_sid = None
                
            except Exception as sms_error:
                print(f"⚠️  Failed to send SMS: {sms_error}\n")
                sms_sent = False
                sms_message_sid = None
        else:
            print("SMS notification skipped.\n")
            sms_sent = False
            sms_message_sid = None
            
    except Exception as e:
        print(f"⚠️  SMS input error: {e}\n")
        sms_sent = False
        sms_message_sid = None
    
    # Validate planning phase output
    validated_planning = planning_result.final_output
    try:
        validated_planning = validate_agent_output("planning", planning_result.final_output)
    except ValueError as e:
        print(f"⚠️  Planning phase schema validation error: {e}")
    
    # Validate all specialist outputs one more time before returning
    validated_specialist_outputs = {}
    for agent_name, output in specialist_outputs.items():
        try:
            validated_specialist_outputs[agent_name] = validate_agent_output(agent_name, output)
        except ValueError as e:
            print(f"⚠️  Final validation error for {agent_name}: {e}")
            validated_specialist_outputs[agent_name] = output
    
    # Parse and validate final_plan before returning
    final_plan_parsed = final_result.final_output
    if isinstance(final_plan_parsed, str):
        try:
            final_plan_parsed = json.loads(final_plan_parsed)
        except json.JSONDecodeError:
            # Try extracting JSON from markdown
            try:
                if '```json' in final_plan_parsed:
                    json_str = final_plan_parsed.split('```json')[1].split('```')[0].strip()
                elif '```' in final_plan_parsed:
                    json_str = final_plan_parsed.split('```')[1].split('```')[0].strip()
                else:
                    import re
                    match = re.search(r'\{.*\}', final_plan_parsed, re.DOTALL)
                    if match:
                        json_str = match.group(0)
                    else:
                        raise ValueError("No JSON found")
                final_plan_parsed = json.loads(json_str)
            except:
                # Don't truncate - preserve full text
                final_plan_parsed = {"executive_summary": final_plan_parsed}
    
    # Validate final_plan has required structure
    if not isinstance(final_plan_parsed, dict):
        # Don't truncate - preserve full text
        final_plan_parsed = {"executive_summary": str(final_plan_parsed)}
    
    # Ensure timeline exists (even if empty)
    if "timeline" not in final_plan_parsed:
        print("⚠️  Warning: Coordinator did not generate timeline in final plan")
        final_plan_parsed["timeline"] = []
    
    # Return comprehensive results
    result = {
        "event_details": event_details,
        "planning_phase": validated_planning,
        "specialist_outputs": validated_specialist_outputs,
        "final_plan": final_plan_parsed,
        "calendar_invite": calendar_result.final_output if calendar_result else json.dumps({"status": "error"}),
        "registration_form": form_data,
        "logo": logo_data,
        "pdf_report": pdf_path,
        "agents_used": required_agents + ["calendar", "form", "logo"],
        "agent_statuses": agent_statuses,
        "success": True,
        "pdf_generated": pdf_generated,
        "sms_sent": sms_sent,
        "sms_message_sid": sms_message_sid
    }
    
    # Restore original input function if we patched it
    if original_input is not None:
        import builtins
        builtins.input = original_input
    
    # Cleanup: close MCP servers and copy files
    try:
        # Properly close MCP server contexts
        if fs_server is not None:
            try:
                loop.run_until_complete(fs_server.__aexit__(None, None, None))
                print("\n🔒 Filesystem MCP server closed.")
            except Exception as e:
                print(f"⚠️  Error closing filesystem server: {e}")
        
        if tally_server is not None:
            try:
                loop.run_until_complete(tally_server.__aexit__(None, None, None))
                print("🔒 Tally MCP server closed.")
            except Exception as e:
                print(f"⚠️  Error closing tally server: {e}")
        
        if SANDBOX_ENABLED and SANDBOX_DIR.exists():
            print("📁 Copying files from sandbox to project...")
            copy_sandbox_files_to_project(SANDBOX_DIR, PROJECT_OUTPUT_DIR)
            print("✅ Sandbox files copied to event_outputs/\n")
    except Exception as cleanup_error:
        print(f"⚠️  Cleanup error: {cleanup_error}")
    
    # Show where calendar file was created
    from pathlib import Path
    calendar_files = list(Path("event_outputs").glob("*.ics"))
    if calendar_files:
        print("=" * 60)
        print("📅 Calendar Files Created:")
        for cf in calendar_files:
            if fs_server is not None:
                print(f"  📡 {cf.name} (via sandboxed MCP)")
            else:
                print(f"  📂 {cf.name} (local file I/O)")
        print("=" * 60 + "\n")
    
    # Log final outputs summary
    logger.info("="*80)
    logger.info("Final Output Summary:")
    for key, value in result.items():
        length = len(str(value)) if value else 0
        logger.info(f"  {key}: {length} chars")
        if length > 0:
            logger.debug(f"  {key} content: {str(value)[:500]}...")
    logger.info("="*80)
    logger.info(f"Workflow complete. Log saved to: {log_file}")
    
    return result


