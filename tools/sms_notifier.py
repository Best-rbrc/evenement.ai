"""SMS notification tool for event planning.

Sends SMS notifications via Twilio with event details and registration form links.
"""
import os
from typing import Dict, Any, Optional


def send_event_sms(
    event_details: Dict[str, Any],
    form_url: Optional[str] = None,
    recipient_phone: Optional[str] = None,
    from_phone: Optional[str] = None
) -> Dict[str, Any]:
    """Send SMS notification for event invitation.
    
    Args:
        event_details: Event information dict with at least 'event_name' and 'event_date'
        form_url: Optional registration form URL to include in SMS
        recipient_phone: Optional recipient phone number (defaults to env var or hardcoded)
        from_phone: Optional sender phone number (defaults to env var or hardcoded)
    
    Returns:
        Dict with:
            - success: bool indicating if SMS was sent successfully
            - message_sid: str Twilio message SID if successful, None otherwise
            - error: str error message if failed, None otherwise
    """
    try:
        from twilio.rest import Client
    except ImportError:
        return {
            "success": False,
            "message_sid": None,
            "error": "Twilio library not installed. Install with: pip install twilio"
        }
    
    # Get Twilio credentials from environment variables with hardcoded defaults
    account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'TWILIO_ACCOUNT_SID_REMOVED')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'TWILIO_AUTH_TOKEN_REMOVED')
    
    # Get phone numbers from parameters, env vars, or defaults
    from_phone_number = from_phone or os.getenv('TWILIO_FROM_PHONE', '+10000000000')
    to_phone_number = recipient_phone or os.getenv('TWILIO_TO_PHONE', '+10000000000')
    
    # Validate credentials
    if not account_sid or not auth_token:
        return {
            "success": False,
            "message_sid": None,
            "error": "Twilio credentials not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables."
        }
    
    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Create SMS body with event details
        event_name = event_details.get('event_name', 'Event')
        event_date = event_details.get('event_date', 'TBD')
        
        if form_url:
            sms_body = f"Hey! You're invited to {event_name} on {event_date}. RSVP: {form_url}"
        else:
            sms_body = f"Hey! You're invited to {event_name} on {event_date}. Form link available soon."
        
        # Send SMS
        message = client.messages.create(
            from_=from_phone_number,
            body=sms_body,
            to=to_phone_number
        )
        
        return {
            "success": True,
            "message_sid": message.sid,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "message_sid": None,
            "error": str(e)
        }

