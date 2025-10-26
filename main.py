"""AI Event Planner - Main application with user input collection and agent coordination."""
import asyncio
from typing import Dict, List, Any
from config import EVENT_TYPES, AGENT_SPECIALIZATIONS
from workflows.plan_generation import produce_actionable_plan
from workflows.coordinator_agent import create_coordinator_agent
from custom_agents.base import create_specialized_agents
import json


class EventPlanner:
    """Main Event Planner class that coordinates all agents."""
    
    def __init__(self):
        self.event_details = {}
        self.required_agents = []
        self.specialized_agents = {}
        
    async def collect_event_details(self) -> Dict[str, Any]:
        """Collect basic event information from the user."""
        print("🎉 Welcome to the AI Event Planner!")
        print("I'll help you plan your event by asking a few key questions.\n")
        
        # Collect basic event information
        event_type = input("What type of event are you planning? (e.g., wedding, corporate conference, tech conference, birthday party, gala dinner, workshop, networking event, product launch, charity fundraiser, retreat): ").strip().lower()
        
        event_name = input("What's the name of your event? ").strip()
        
        event_date = input("When is your event? (e.g., 'March 15, 2024' or 'Q2 2024'): ").strip()
        
        location_preference = input("Do you have a preferred location or city? (or 'flexible'): ").strip()
        
        budget_range = input("What's your approximate budget range? (e.g., '$5,000-$10,000', 'under $2,000', 'flexible'): ").strip()
        
        guest_count = input("How many guests/attendees are you expecting? (e.g., '50-100', '200+', 'flexible'): ").strip()
        
        special_requirements = input("Any special requirements or themes? (e.g., 'outdoor venue', 'vegetarian catering', 'accessibility needs', 'corporate theme'): ").strip()
        
        # Store event details
        self.event_details = {
            "event_type": event_type,
            "event_name": event_name,
            "event_date": event_date,
            "location_preference": location_preference,
            "budget_range": budget_range,
            "guest_count": guest_count,
            "special_requirements": special_requirements
        }
        
        return self.event_details
    
    def determine_required_agents(self) -> List[str]:
        """Determine which specialized agents are needed based on event type."""
        event_type = self.event_details.get("event_type", "")
        
        # Map user input to our predefined event types
        event_type_mapping = {
            "wedding": "wedding",
            "corporate conference": "corporate_conference", 
            "corporate": "corporate_conference",
            "conference": "corporate_conference",
            "tech conference": "tech_conference",
            "tech": "tech_conference",
            "birthday party": "birthday_party",
            "birthday": "birthday_party",
            "party": "birthday_party",
            "gala dinner": "gala_dinner",
            "gala": "gala_dinner",
            "dinner": "gala_dinner",
            "workshop": "workshop",
            "networking event": "networking_event",
            "networking": "networking_event",
            "product launch": "product_launch",
            "launch": "product_launch",
            "charity fundraiser": "charity_fundraiser",
            "fundraiser": "charity_fundraiser",
            "charity": "charity_fundraiser",
            "retreat": "retreat"
        }
        
        mapped_type = event_type_mapping.get(event_type, "corporate_conference")
        
        if mapped_type in EVENT_TYPES:
            self.required_agents = EVENT_TYPES[mapped_type]
        else:
            # Default to a comprehensive set for unknown event types
            self.required_agents = ["venue", "catering", "communication", "programme"]
        
        print(f"\n📋 Based on your {event_type} event, I'll coordinate these specialized agents:")
        for agent in self.required_agents:
            print(f"  • {agent.title()} Agent: {AGENT_SPECIALIZATIONS.get(agent, 'Specialized planning')}")
        
        return self.required_agents
    
    async def initialize_agents(self):
        """Initialize the coordinator and specialized agents."""
        print("\n🤖 Initializing AI agents...")
        
        # Create specialized agents
        self.specialized_agents = create_specialized_agents(self.required_agents)
        # Debug: print types of the created specialized agents to ensure they're Agent instances
        print("\nDebug: specialized_agents contents:")
        for k, v in self.specialized_agents.items():
            try:
                r = repr(v)
            except Exception:
                r = str(type(v))
            print(f"  - {k}: type={type(v)}, repr={r[:200]}")
        
        # Create coordinator agent
        self.coordinator = create_coordinator_agent(
            self.event_details, 
            self.required_agents, 
            self.specialized_agents
        )
        
        print("✅ All agents initialized and ready!")
    
    async def run_planning_session(self):
        """Run the planning session using the Coordinator Agent."""
        print(f"\n🚀 Starting planning session for '{self.event_details['event_name']}'...\n")
        try:
            plan = await produce_actionable_plan(self.coordinator, self.event_details, self.required_agents)
            return plan
        except Exception as e:
            print(f"❌ Error producing plan: {e}")
            return None

    
    def run(self):
        """Main execution method."""
        try:
            # Collect event details
            asyncio.run(self.collect_event_details())
            
            # Determine required agents
            self.determine_required_agents()
            
            # Initialize agents
            asyncio.run(self.initialize_agents())
            
            # Run planning session
            result = asyncio.run(self.run_planning_session())
            
            if result:
                print("\n" + "="*60)
                print("📋 EVENT PLANNING RESULTS")
                print("="*60)
                # If result is a dict (our no-timeline plan), pretty print JSON
                if isinstance(result, dict):
                    print(json.dumps(result, indent=2))
                else:
                    # fallback to previous behavior
                    try:
                        print(result.final_output)
                    except Exception:
                        print(result)
                print("="*60)
            else:
                print("❌ Planning session failed. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Planning session cancelled by user.")
        except Exception as e:
            print(f"❌ An error occurred: {e}")


def main():
    """Main entry point."""
    planner = EventPlanner()
    planner.run()


if __name__ == "__main__":
    main()
