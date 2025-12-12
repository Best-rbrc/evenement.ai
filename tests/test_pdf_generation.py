"""Test PDF report generation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.report_generator import generate_event_proposal_pdf
import json
from datetime import datetime


def test_pdf_generation():
    """Test generating a PDF report with sample data."""
    
    print("="*60)
    print("Testing PDF Report Generation")
    print("="*60)
    
    # Sample event details
    event_details = {
        "event_name": "Tech Innovation Summit 2025",
        "event_type": "tech conference",
        "event_date": "March 15-16, 2025",
        "location_preference": "San Francisco Bay Area",
        "budget_range": "$50,000-$75,000",
        "guest_count": "200-250",
        "special_requirements": "Need 3 parallel tracks, keynote speakers, workshop spaces, networking areas"
    }
    
    # Sample final plan
    final_plan = {
        "executive_summary": """This comprehensive event plan outlines a two-day tech innovation summit designed to bring together 200-250 technology leaders, innovators, and professionals. The event will feature three parallel tracks covering AI/ML, Cloud Computing, and Cybersecurity, with keynote presentations, workshops, and extensive networking opportunities.

The venue selection prioritizes modern conference facilities in the San Francisco Bay Area with capacity for 300+ attendees across multiple rooms. The budget allocation ensures high-quality catering, top-tier speakers, and professional production values while maintaining a 12% contingency fund.

Key success factors include early speaker confirmation, robust registration system, and seamless coordination across all parallel tracks. Risk mitigation strategies address potential speaker cancellations, technical issues, and attendance fluctuations.""",
        
        "timeline": [
            {
                "phase": "Pre-Event (4-6 weeks)",
                "tasks": [
                    "Finalize venue contract and room assignments",
                    "Confirm all speakers and travel arrangements",
                    "Launch registration system and marketing campaign",
                    "Order AV equipment and technical setup",
                    "Finalize catering menu and dietary accommodations"
                ],
                "deadline": "February 15, 2025"
            },
            {
                "phase": "Week Before Event",
                "tasks": [
                    "Final attendee count to caterer",
                    "Print conference materials and signage",
                    "Brief all volunteers and staff",
                    "Tech rehearsal with speakers",
                    "Set up registration area"
                ],
                "deadline": "March 8, 2025"
            },
            {
                "phase": "Event Days",
                "tasks": [
                    "Day 1: Registration, keynote, parallel sessions, networking reception",
                    "Day 2: Workshops, panel discussions, closing keynote",
                    "Continuous: Tech support, attendee assistance, social media updates"
                ],
                "deadline": "March 15-16, 2025"
            },
            {
                "phase": "Post-Event",
                "tasks": [
                    "Gather attendee feedback surveys",
                    "Process speaker payment and thank yous",
                    "Compile event photos and videos",
                    "Generate ROI report for stakeholders",
                    "Post-mortem meeting with team"
                ],
                "deadline": "March 31, 2025"
            }
        ],
        
        "schedule": {
            "optimized": True,
            "sessions": [
                {
                    "session_id": 1,
                    "session_name": "Opening Keynote: The Future of AI",
                    "start_time": "09:00",
                    "end_time": "10:00",
                    "room": "Main Auditorium",
                    "speaker": "Dr. Sarah Chen",
                    "expected_attendees": 250
                },
                {
                    "session_id": 2,
                    "session_name": "AI Track: Machine Learning Best Practices",
                    "start_time": "10:30",
                    "end_time": "11:30",
                    "room": "Track A",
                    "speaker": "Prof. Michael Rodriguez",
                    "expected_attendees": 80
                },
                {
                    "session_id": 3,
                    "session_name": "Cloud Track: Kubernetes at Scale",
                    "start_time": "10:30",
                    "end_time": "11:30",
                    "room": "Track B",
                    "speaker": "Jane Wilson",
                    "expected_attendees": 70
                },
                {
                    "session_id": 4,
                    "session_name": "Security Track: Zero Trust Architecture",
                    "start_time": "10:30",
                    "end_time": "11:30",
                    "room": "Track C",
                    "speaker": "David Park",
                    "expected_attendees": 60
                }
            ],
            "metrics": {
                "total_duration": "8h 30m",
                "event_ends_at": "17:30",
                "room_utilization": {
                    "Main Auditorium": "45.5%",
                    "Track A": "68.2%",
                    "Track B": "65.8%",
                    "Track C": "62.3%"
                },
                "conflicts_resolved": "All room and speaker conflicts resolved via constraint optimization"
            },
            "status": "optimal"
        },
        
        "budget": {
            "total_available": "$75,000",
            "total_allocated": "$66,000",
            "by_category": {
                "venue": "$18,000",
                "catering": "$15,000",
                "speakers": "$12,000",
                "av_equipment": "$6,000",
                "marketing": "$4,000",
                "materials": "$3,000",
                "contingency": "$8,000"
            },
            "status": "within_budget"
        },
        
        "recommendations": {
            "venue": {
                "top_choice": "San Francisco Convention Center",
                "capacity": "300+",
                "features": ["Multiple breakout rooms", "Built-in AV", "Catering kitchen", "High-speed WiFi"],
                "cost": "$18,000 for 2 days"
            },
            "catering": {
                "provider": "Bay Area Catering Co.",
                "menu": "Continental breakfast, lunch buffet, afternoon snacks, networking reception",
                "dietary_options": "Vegetarian, vegan, gluten-free, kosher",
                "cost_per_person": "$60/day"
            },
            "speakers": {
                "confirmed": ["Dr. Sarah Chen", "Prof. Michael Rodriguez"],
                "pending": ["Jane Wilson", "David Park"],
                "honorariums": "$2,000-$5,000 per speaker plus travel",
                "total_estimated": "$12,000"
            }
        },
        
        "risks": [
            {
                "risk": "Keynote speaker cancellation",
                "severity": "high",
                "mitigation": "Have backup speakers on standby, include cancellation clause in contracts, maintain speaker waitlist"
            },
            {
                "risk": "Technical failures during presentations",
                "severity": "medium",
                "mitigation": "On-site tech support team, backup equipment, pre-event tech checks with all speakers"
            },
            {
                "risk": "Lower than expected attendance",
                "severity": "medium",
                "mitigation": "Early bird pricing, group discounts, targeted marketing campaigns, flexible catering adjustments"
            },
            {
                "risk": "Scheduling conflicts between tracks",
                "severity": "low",
                "mitigation": "Constraint optimization already applied, buffer time between sessions, clear signage"
            }
        ],
        
        "action_items": [
            {
                "action": "Sign venue contract and pay deposit",
                "owner": "Operations Manager",
                "deadline": "January 15, 2025",
                "priority": "high"
            },
            {
                "action": "Finalize speaker lineup and send contracts",
                "owner": "Programme Director",
                "deadline": "January 30, 2025",
                "priority": "high"
            },
            {
                "action": "Launch registration website",
                "owner": "Marketing Team",
                "deadline": "February 1, 2025",
                "priority": "high"
            },
            {
                "action": "Order AV equipment and arrange tech support",
                "owner": "Technical Lead",
                "deadline": "February 15, 2025",
                "priority": "medium"
            },
            {
                "action": "Finalize catering menu and headcount",
                "owner": "Catering Coordinator",
                "deadline": "March 1, 2025",
                "priority": "medium"
            },
            {
                "action": "Print conference materials and badges",
                "owner": "Operations Team",
                "deadline": "March 8, 2025",
                "priority": "low"
            }
        ],
        
        "assumptions": [
            "Venue availability on proposed dates",
            "Speaker availability and acceptance of terms",
            "80% registration conversion rate",
            "No major conflicting events in the area",
            "Standard tech requirements for all presentations"
        ]
    }
    
    # Generate PDF
    print("\n Generating PDF report...\n")
    
    try:
        pdf_path = generate_event_proposal_pdf(
            event_details=event_details,
            final_plan=final_plan,
            output_dir="event_outputs"
        )
        
        print(f" SUCCESS!")
        print(f"\n PDF Report Generated:")
        print(f"   Path: {pdf_path}")
        print(f"\n Open the file to view the professional event proposal.")
        
        # Display report structure
        print(f"\n Report Contents:")
        print(f"   1. Cover Page with Event Details")
        print(f"   2. Table of Contents")
        print(f"   3. Executive Summary")
        print(f"   4. Event Overview")
        print(f"   5. Timeline (Gantt-style)")
        print(f"   6. Budget Breakdown with Charts")
        print(f"   7. Detailed Recommendations")
        print(f"   8. Optimized Schedule (from OR-Tools)")
        print(f"   9. Risk Assessment Matrix")
        print(f"   10. Action Items Checklist")
        
        return True
        
    except Exception as e:
        print(f" FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print(" PDF Report Generation Test\n")
    
    success = test_pdf_generation()
    
    if success:
        print("\n\n Test completed successfully!")
    else:
        print("\n\n Test failed - check errors above")
