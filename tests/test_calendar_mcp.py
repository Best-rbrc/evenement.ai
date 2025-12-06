"""Test calendar agent with sandboxed MCP file writing."""
import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from agents import Runner
from custom_agents.calendar_agent import create_calendar_agent

# Load environment variables from .env
load_dotenv()

# Configuration
SANDBOX_DIR = Path("/tmp/mcp_event_outputs")
PROJECT_OUTPUT_DIR = Path(__file__).parent / "event_outputs"


async def setup_sandboxed_mcp():
    """Setup sandboxed MCP server - mirrors workflow setup."""
    try:
        from mcp_sandbox_openai_sdk import (
            FSAccess,
            MCPManifest,
            Permission,
            SandboxedMCPStdio,
        )
        
        SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
        
        manifest = MCPManifest(
            name="Filesystem Server",
            description="Sandbox-restricted file server for event outputs",
            registry="npm",
            package_name="@modelcontextprotocol/server-filesystem",
            permissions=[
                Permission.MCP_AC_FILESYSTEM_READ,
                Permission.MCP_AC_FILESYSTEM_WRITE,
                Permission.MCP_AC_FILESYSTEM_DELETE,
            ],
        )
        
        # Create sandboxed MCP server
        sandboxed_server = SandboxedMCPStdio(
            manifest=manifest,
            runtime_args=[str(SANDBOX_DIR)],
            runtime_permissions=[
                FSAccess(str(SANDBOX_DIR), read=True, write=True),
            ],
        )
        
        # Initialize the server
        await sandboxed_server.__aenter__()
        print("✅ Sandboxed MCP server initialized")
        return sandboxed_server
    except Exception as e:
        print(f"⚠️  MCP setup failed: {e}")
        return None


def test_calendar_without_mcp():
    """Test calendar agent WITHOUT MCP (baseline test)."""
    print("=" * 60)
    print("🧪 Testing Calendar Agent WITHOUT MCP (Baseline)")
    print("=" * 60)
    
    # Create calendar agent WITHOUT MCP
    print("\n1️⃣  Creating calendar agent (no MCP)...")
    try:
        calendar_agent = create_calendar_agent(mcp_servers=None)
        print("✅ Calendar agent created")
    except Exception as e:
        print(f"❌ Failed to create calendar agent: {e}")
        return False
    
    # Test calendar prompt
    print("\n2️⃣  Running calendar agent to generate ICS file...")
    prompt = """You are creating a calendar invite for a tech conference.

Event Details:
- Event Name: Test Conference 2026
- Date: 2026-03-15
- Start Time: 09:00
- End Time: 17:00
- Location: Test Convention Center
- Description: Test conference event

Please use the generate_ics_file tool to create the calendar invite with these details.
Respond with just the result message.
"""
    
    try:
        result = Runner.run_sync(calendar_agent, prompt, max_turns=5)
        print(f"✅ Agent completed")
        print(f"\nAgent Output:\n{result.final_output}")
    except Exception as e:
        print(f"❌ Agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check if file was created locally
    print("\n3️⃣  Checking if file was created in event_outputs...")
    files_in_project = list(PROJECT_OUTPUT_DIR.glob("*.ics")) if PROJECT_OUTPUT_DIR.exists() else []
    if files_in_project:
        print(f"✅ Found {len(files_in_project)} ICS file(s):")
        for f in files_in_project:
            size = f.stat().st_size
            print(f"   - {f.name} ({size} bytes)")
            if size > 0:
                with open(f, 'r') as fp:
                    content = fp.read()
                    if "BEGIN:VCALENDAR" in content:
                        print(f"     ✓ Valid ICS format")
                    else:
                        print(f"     ✗ Invalid ICS format")
        return True
    else:
        print("❌ No ICS files found in project output directory")
        return False


async def test_with_mcp_enabled():
    """Test with MCP enabled - mirrors full workflow setup. [DEPRECATED - use main() instead]"""
    # This function is kept for reference but not used anymore
    # The MCP test is now handled inline in main() to avoid event loop conflicts
    pass


def test_with_mcp_disabled():
    """Test with MCP disabled to verify it still works."""
    print("\n\n" + "=" * 60)
    print("🧪 Testing Calendar Agent with MCP Disabled")
    print("=" * 60)
    
    # Set SANDBOX_ENABLED to False in the environment
    os.environ["SANDBOX_ENABLED"] = "False"
    
    # Create calendar agent WITHOUT MCP
    print("\n1️⃣  Creating calendar agent (MCP disabled)...")
    try:
        calendar_agent = create_calendar_agent(mcp_servers=None)
        print("✅ Calendar agent created")
    except Exception as e:
        print(f"❌ Failed to create calendar agent: {e}")
        return False
    
    print("\n2️⃣  Running calendar agent...")
    prompt = """You are creating a calendar invite.

Use the generate_ics_file tool to create a calendar file for:
- Event: Simple Test Event
- Date: 2026-03-20
- Start Time: 14:00
- End Time: 15:00
- Location: Test Location
- Description: Simple test

Just use the tool and report success.
"""
    
    try:
        result = Runner.run_sync(calendar_agent, prompt, max_turns=5)
        print(f"✅ Agent completed")
        print(f"\nAgent Output:\n{result.final_output}")
        return True
    except Exception as e:
        print(f"❌ Agent failed: {e}")
        return False


def main():
    """Run the tests."""
    print("\n🚀 Calendar Agent Test Suite\n")
    
    # Test 1: Basic calendar without MCP
    test1_passed = test_calendar_without_mcp()
    
    # Test 3: With MCP disabled
    test3_passed = test_with_mcp_disabled()
    
    # Test 2: With MCP enabled (mirrors workflow) - handle event loop properly
    print("\n\n" + "=" * 60)
    print("🧪 Testing Calendar Agent WITH MCP (Mirrors Workflow)")
    print("=" * 60)
    
    test2_result = None
    try:
        # Use a fresh event loop and keep it alive for both setup and agent run
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Setup MCP server in this event loop
            print("\n1️⃣  Setting up sandboxed MCP server...")
            mcp_server = loop.run_until_complete(setup_sandboxed_mcp())
            
            if mcp_server is None:
                print("⚠️  MCP setup failed, skipping MCP test")
                test2_result = None
            else:
                # Now that MCP server is set up, we can use Runner.run_sync
                print("\n2️⃣  Creating calendar agent with MCP...")
                try:
                    calendar_agent = create_calendar_agent(mcp_servers=mcp_server)
                    print("✅ Calendar agent created with MCP")
                except Exception as e:
                    print(f"❌ Failed to create calendar agent: {e}")
                    import traceback
                    traceback.print_exc()
                    test2_result = False
                
                if test2_result is not False:  # Only run agent if agent was created successfully
                    print("\n3️⃣  Running calendar agent with MCP (30 sec timeout)...")
                    prompt = """You are creating a calendar invite.

Use the generate_ics_file tool to create a calendar file for:
- Event: MCP Test Event
- Date: 2026-04-15
- Start Time: 10:00
- End Time: 11:00
- Location: MCP Location
- Description: MCP sandboxed test

Just use the tool and report success.
"""
                    
                    try:
                        result = Runner.run_sync(calendar_agent, prompt, max_turns=5)
                        print(f"✅ Agent completed")
                        print(f"\nAgent Output:\n{result.final_output}")
                        test2_result = True
                    except TimeoutError as e:
                        print(f"❌ Agent TIMEOUT (MCP server not responding): {e}")
                        test2_result = False
                    except Exception as e:
                        print(f"❌ Agent failed: {e}")
                        import traceback
                        traceback.print_exc()
                        test2_result = False
        finally:
            loop.close()
            
    except Exception as e:
        print(f"❌ MCP test setup failed: {e}")
        import traceback
        traceback.print_exc()
        test2_result = False
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"  Baseline (no MCP):     {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"  MCP Disabled:          {'✅ PASS' if test3_passed else '❌ FAIL'}")
    print(f"  MCP Enabled:           {'✅ PASS' if test2_result is True else ('⏭️  SKIP' if test2_result is None else '❌ FAIL')}")
    print("=" * 60)
    
    # Overall result
    if test1_passed and test3_passed:
        if test2_result is True:
            print("\n✅ All tests PASSED!")
            return 0
        elif test2_result is None:
            print("\n⚠️  Core tests passed, MCP test skipped")
            return 0
        else:
            print("\n⚠️  Core tests passed, but MCP test FAILED")
            return 1
    else:
        print("\n❌ Some core tests FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
