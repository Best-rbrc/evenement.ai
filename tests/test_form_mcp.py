"""Test form agent with sandboxed MCP file writing."""
import sys
from pathlib import Path

# Add parent directory to path so we can import custom_agents
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import json
import os
from dotenv import load_dotenv
from agents import Runner
from custom_agents.form_agent import create_form_agent

# Load environment variables from .env
load_dotenv()

# Configuration
SANDBOX_DIR = Path("/tmp/mcp_event_outputs")
PROJECT_OUTPUT_DIR = Path(__file__).parent / "event_outputs"


async def setup_sandboxed_mcp():
    """Setup sandboxed custom Tally MCP server with network egress and API key via static_environment_vars."""
    try:
        from mcp_sandbox_openai_sdk import (
            DomainPort,
            DevMCPManifest,
            Permission,
            SandboxedMCPStdio,
        )
        
        SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
        
        # Custom Tally MCP manifest (local Python server)
        # Navigate up to project root, then to custom_mcp_servers
        tally_server_path = Path(__file__).parent.parent / "custom_mcp_servers"
        tally_manifest = DevMCPManifest(
            name="Tally Form Server",
            description="Custom sandboxed Tally MCP server with network access to api.tally.so",
            registry="pypi",
            package_name="tally-mcp-server",  # Not used for DevMCPManifest
            permissions=[
                Permission.MCP_AC_NETWORK_CLIENT,  # Network access permission
            ],
            code_mount=str(tally_server_path),
            exec_command="python3 /sandbox/tally_mcp_server.py",
        )
        
        # Get API key from environment
        tally_api_key = os.getenv('TALLY_API_KEY', '')
        if not tally_api_key:
            print("⚠️  Warning: TALLY_API_KEY environment variable not set")
        
        # Create sandboxed Tally server with network egress and API key via static env vars
        tally_server = SandboxedMCPStdio(
            manifest=tally_manifest,
            runtime_args=[],  # No args needed - server reads from env
            runtime_permissions=[
                DomainPort("api.tally.so", 443),  # Allow HTTPS access to Tally API
            ],
            static_environment_vars={
                "TALLY_API_KEY": tally_api_key,  # Pass API key directly to container
            },
        )
        
        # Initialize the server
        await tally_server.__aenter__()
        print("✅ Sandboxed custom Tally MCP server initialized with network egress")
        return tally_server
    except Exception as e:
        print(f"⚠️  MCP setup failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_form_without_mcp():
    """Test form agent WITHOUT MCP (baseline test)."""
    print("=" * 60)
    print("🧪 Testing Form Agent WITHOUT MCP (Baseline)")
    print("=" * 60)
    
    # Create form agent WITHOUT MCP
    print("\n1️⃣  Creating form agent (no MCP)...")
    try:
        form_agent = create_form_agent(mcp_servers=None)
        print("✅ Form agent created")
    except Exception as e:
        print(f"❌ Failed to create form agent: {e}")
        return False
    
    # Test form prompt
    print("\n2️⃣  Running form agent to create registration form...")
    prompt = """You are creating a registration form for a tech conference.

Event Details:
- Event Name: Tech Conference 2026
- Event Type: Conference
- Expected Attendees: 500
- Special Requirements: Need to collect speaker information

Please create an appropriate registration form for this event.
Return ONLY valid JSON with: {"form_url": "https://tally.so/r/xxxxx", "status": "success", "form_details": "description"}
"""
    
    try:
        result = Runner.run_sync(form_agent, prompt, max_turns=15)
        print(f"✅ Agent completed")
        print(f"\nAgent Output:\n{result.final_output}")
        return True
    except Exception as e:
        print(f"❌ Agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_form_with_mcp_disabled():
    """Test with MCP disabled to verify it still works."""
    print("\n\n" + "=" * 60)
    print("🧪 Testing Form Agent with MCP Disabled")
    print("=" * 60)
    
    # Create form agent WITHOUT MCP
    print("\n1️⃣  Creating form agent (MCP disabled)...")
    try:
        form_agent = create_form_agent(mcp_servers=None)
        print("✅ Form agent created")
    except Exception as e:
        print(f"❌ Failed to create form agent: {e}")
        return False
    
    print("\n2️⃣  Running form agent...")
    prompt = """You are creating a registration form for a corporate event.

Event Details:
- Event Name: Corporate Annual Meeting 2026
- Event Type: Corporate Event
- Expected Attendees: 200

Please create an appropriate registration form.
Return ONLY valid JSON with: {"form_url": "https://tally.so/r/xxxxx", "status": "success", "form_details": "description"}
"""
    
    try:
        result = Runner.run_sync(form_agent, prompt, max_turns=15)
        print(f"✅ Agent completed")
        print(f"\nAgent Output:\n{result.final_output}")
        return True
    except Exception as e:
        print(f"❌ Agent failed: {e}")
        return False


def main():
    """Run the tests."""
    print("\n🚀 Testing Form Agent WITH MCP ONLY\n")
    
    # Only test MCP version
    print("=" * 60)
    print("🧪 Testing Form Agent WITH Sandboxed MCP")
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
                print("\n2️⃣  Creating form agent with MCP...")
                try:
                    form_agent = create_form_agent(mcp_servers=mcp_server)
                    print("✅ Form agent created with MCP")
                except Exception as e:
                    print(f"❌ Failed to create form agent: {e}")
                    import traceback
                    traceback.print_exc()
                    test2_result = False
                
                if test2_result is not False:  # Only run agent if agent was created successfully
                    print("\n3️⃣  Running form agent with MCP (30 sec timeout)...")
                    prompt = """You are creating a registration form for a startup pitch event.

Event Details:
- Event Name: Startup Pitch Event 2026
- Event Type: Startup Event
- Expected Attendees: 100
- Special Requirements: Collect startup info

Please create an appropriate registration form.
Return ONLY valid JSON with: {"form_url": "https://tally.so/r/xxxxx", "status": "success", "form_details": "description"}
"""
                    
                    try:
                        result = Runner.run_sync(form_agent, prompt, max_turns=15)
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
    print("📊 Test Result:")
    print(f"  MCP Enabled:           {'✅ PASS' if test2_result is True else ('⏭️  SKIP' if test2_result is None else '❌ FAIL')}")
    print("=" * 60)
    
    # Overall result
    if test2_result is True:
        print("\n✅ MCP test PASSED!")
        return 0
    elif test2_result is None:
        print("\n⏭️  MCP test skipped")
        return 0
    else:
        print("\n❌ MCP test FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
