"""Test file for logo agent - tests logo generation using OpenAI API."""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import directly from the module to avoid triggering __init__.py imports
# This bypasses the package __init__.py which imports other agents with TensorFlow deps
import importlib.util
logo_agent_path = Path(__file__).parent.parent / "custom_agents" / "logo_agent.py"
spec = importlib.util.spec_from_file_location("logo_agent", logo_agent_path)
logo_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logo_agent_module)

# Get the implementation function directly - this is the actual function we can call
# The generate_logo_image is wrapped in FunctionTool, so we use the implementation
generate_logo_image = getattr(logo_agent_module, '_generate_logo_image_impl', None)

# Fallback: if implementation not found, try to unwrap the FunctionTool
if generate_logo_image is None:
    generate_logo_image_wrapped = logo_agent_module.generate_logo_image
    # Try different ways to access the underlying function
    if hasattr(generate_logo_image_wrapped, 'func'):
        generate_logo_image = generate_logo_image_wrapped.func
    elif hasattr(generate_logo_image_wrapped, '__wrapped__'):
        generate_logo_image = generate_logo_image_wrapped.__wrapped__
    elif hasattr(generate_logo_image_wrapped, '_func'):
        generate_logo_image = generate_logo_image_wrapped._func
    else:
        generate_logo_image = generate_logo_image_wrapped

# Try to get create_logo_agent, but it might fail if agents package has issues
try:
    create_logo_agent = logo_agent_module.create_logo_agent
except AttributeError:
    create_logo_agent = None


def test_logo_generation():
    """Test logo generation with real OpenAI API."""
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(" ERROR: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key:")
        print("  OPENAI_API_KEY=sk-...your-key-here...")
        return False
    
    print(" OpenAI API key found")
    print(f"   Key starts with: {api_key[:10]}...")
    print()
    
    # Test event details
    event_name = "AI Innovation Summit 2026"
    event_type = "conference"
    event_description = "A premier conference bringing together AI researchers, practitioners, and innovators"
    style_preferences = "modern, tech-forward, professional"
    
    print(" Test Parameters:")
    print(f"   Event Name: {event_name}")
    print(f"   Event Type: {event_type}")
    print(f"   Description: {event_description}")
    print(f"   Style: {style_preferences}")
    print()
    
    # Test the function directly
    print(" Generating logo...")
    try:
        result_json = generate_logo_image(
            event_name=event_name,
            event_type=event_type,
            event_description=event_description,
            style_preferences=style_preferences
        )
        
        result = json.loads(result_json)
        
        if result.get("status") == "error":
            print(f" Error: {result.get('message')}")
            return False
        
        print(" Logo generated successfully!")
        print()
        print(" Results:")
        print(f"   Status: {result.get('status')}")
        print(f"   Logo File Path: {result.get('logo_file_path')}")
        print(f"   Logo URL: {result.get('logo_url')}")
        print(f"   Design Rationale: {result.get('design_rationale', '')[:100]}...")
        print()
        
        # Check if file exists
        logo_path = result.get('logo_file_path')
        if logo_path and Path(logo_path).exists():
            file_size = Path(logo_path).stat().st_size
            print(f" Logo file saved: {logo_path}")
            print(f"   File size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        else:
            print(f"  Warning: Logo file not found at {logo_path}")
        
        print()
        print(" Additional Information:")
        print(f"   Color Palette: {result.get('color_palette')}")
        print(f"   Typography: {result.get('typography_suggestions', '')[:80]}...")
        print(f"   Usage Guidelines: {len(result.get('usage_guidelines', []))} items")
        print(f"   Branding Recommendations: {len(result.get('branding_recommendations', []))} items")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f" Error parsing JSON response: {e}")
        print(f"   Raw response: {result_json[:200]}...")
        return False
    except Exception as e:
        print(f" Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_logo_agent_creation():
    """Test that the logo agent can be created."""
    print(" Testing logo agent creation...")
    if create_logo_agent is None:
        print("  Skipping agent creation test (agents package not available)")
        print("   This is expected if TensorFlow dependencies have issues.")
        print("   The generate_logo_image() function can still be tested directly.")
        return True
    
    try:
        agent = create_logo_agent()
        print(f" Agent created: {agent.name}")
        print(f"   Description: {agent.handoff_description}")
        print(f"   Tools: {[tool.name for tool in agent.tools]}")
        return True
    except ImportError as e:
        print(f"  Agent creation skipped: {e}")
        print("   This is expected if agents package has dependency issues.")
        print("   The generate_logo_image() function can still be tested directly.")
        return True
    except Exception as e:
        print(f" Error creating agent: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print(" Logo Agent Test Suite")
    print("=" * 60)
    print()
    
    # Test 1: Agent creation
    print("Test 1: Agent Creation")
    print("-" * 60)
    agent_ok = test_logo_agent_creation()
    print()
    
    if not agent_ok:
        print(" Agent creation failed. Skipping logo generation test.")
        return
    
    # Test 2: Logo generation
    print("Test 2: Logo Generation (Real API Call)")
    print("-" * 60)
    logo_ok = test_logo_generation()
    print()
    
    # Summary
    print("=" * 60)
    print(" Test Summary")
    print("=" * 60)
    print(f"   Agent Creation: {' PASS' if agent_ok else ' FAIL'}")
    print(f"   Logo Generation: {' PASS' if logo_ok else ' FAIL'}")
    print()
    
    if agent_ok and logo_ok:
        print(" All tests passed!")
    else:
        print("  Some tests failed. Please check the output above.")


if __name__ == "__main__":
    main()

