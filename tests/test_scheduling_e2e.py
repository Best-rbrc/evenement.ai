"""End-to-end test for scheduling agent integration in full workflow."""
import json
from workflows.event_planning_workflow import run_event_planning


def test_conference_with_scheduling():
    """Test a multi-session conference that should trigger scheduling optimization."""
    print("="*60)
    print("E2E Test: Tech Conference with Scheduling Optimization")
    print("="*60)
    
    # Event that should trigger scheduling agent
    event_details = {
        "event_name": "AI & ML Summit 2025",
        "event_type": "tech conference",
        "event_date": "March 15, 2025",
        "location_preference": "San Francisco Bay Area",
        "budget_range": "$50,000-$75,000",
        "guest_count": "200-250",
        "special_requirements": "Need 3 parallel tracks, 8 sessions total, keynote speaker, workshop spaces, lunch break at noon"
    }
    
    print("\nEvent Details:")
    print(json.dumps(event_details, indent=2))
    print("\n" + "="*60)
    print("Running full workflow...\n")
    
    result = run_event_planning(event_details)
    
    # Parse final plan to check if scheduling metrics are included
    try:
        final_plan = json.loads(result['final_plan'])
        
        print("\n" + "="*60)
        print("VERIFICATION CHECKS")
        print("="*60)
        
        # Check 1: Was scheduling agent used?
        agents_used = result.get('agents_used', [])
        scheduling_used = 'scheduling' in agents_used
        print(f"\n✓ Scheduling agent used: {scheduling_used}")
        
        # Check 2: Does final plan have schedule section?
        has_schedule_section = 'schedule' in final_plan
        print(f"✓ Final plan has 'schedule' section: {has_schedule_section}")
        
        if has_schedule_section:
            schedule = final_plan['schedule']
            
            # Check 3: Are metrics present?
            has_metrics = 'metrics' in schedule
            print(f"✓ Schedule has metrics: {has_metrics}")
            
            if has_metrics:
                metrics = schedule['metrics']
                print(f"\n📊 SCHEDULING METRICS:")
                print(f"   - Total duration: {metrics.get('total_duration', 'N/A')}")
                print(f"   - Event ends at: {metrics.get('event_ends_at', 'N/A')}")
                print(f"   - Conflicts resolved: {metrics.get('conflicts_resolved', 'N/A')}")
                
                if 'room_utilization' in metrics:
                    print(f"   - Room utilization:")
                    for room, util in metrics['room_utilization'].items():
                        print(f"      • {room}: {util}")
            
            # Check 4: Are sessions included?
            has_sessions = 'sessions' in schedule and len(schedule.get('sessions', [])) > 0
            print(f"\n✓ Optimized sessions included: {has_sessions}")
            if has_sessions:
                print(f"   - Number of sessions: {len(schedule['sessions'])}")
                print(f"   - Sample session: {schedule['sessions'][0].get('session_name', 'N/A')}")
            
            # Check 5: Status
            status = schedule.get('status', 'unknown')
            print(f"\n✓ Schedule status: {status}")
        
        # Check 6: Budget section present?
        has_budget = 'budget' in final_plan
        print(f"\n✓ Final plan has budget section: {has_budget}")
        
        if has_budget:
            budget = final_plan['budget']
            print(f"   - Budget status: {budget.get('status', 'N/A')}")
            print(f"   - Total allocated: {budget.get('total_allocated', 'N/A')}")
        
        print("\n" + "="*60)
        print("✅ E2E TEST COMPLETE")
        print("="*60)
        
        # Save full result to file for inspection
        with open('test_scheduling_e2e_result.json', 'w') as f:
            json.dump({
                'event_details': event_details,
                'agents_used': result.get('agents_used', []),
                'final_plan': final_plan
            }, f, indent=2)
        
        print("\n💾 Full result saved to: test_scheduling_e2e_result.json")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Failed to parse final plan as JSON: {e}")
        print("\nRaw final_plan output:")
        print(result.get('final_plan', 'N/A')[:500] + "...")
        return False


if __name__ == "__main__":
    print("🧪 End-to-End Scheduling Integration Test\n")
    
    try:
        success = test_conference_with_scheduling()
        
        if success:
            print("\n\n✅ All integration checks passed!")
        else:
            print("\n\n⚠️  Some checks failed - see output above")
            
    except Exception as e:
        print(f"\n\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
