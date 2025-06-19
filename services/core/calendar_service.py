import os
from typing import Dict, Optional
from solar.access import public

class CalendarService:
    def __init__(self):
        self.calendly_api_key = os.getenv("CALENDLY_API_KEY")
        self.calendly_username = os.getenv("CALENDLY_USERNAME", "your-calendly-username")
    
    def get_booking_link(self) -> str:
        """Get the Calendly booking link for strategy calls."""
        # Return a standard Calendly link format
        # In production, this could be customized based on user data
        return f"https://calendly.com/{self.calendly_username}/strategy-call"
    
    def get_custom_booking_link(self, business_name: str, proposal_id: str) -> str:
        """Get a customized booking link with pre-filled information."""
        base_link = self.get_booking_link()
        
        # Add URL parameters for pre-filling form data
        params = f"?name={business_name.replace(' ', '%20')}&notes=Proposal%20ID:%20{proposal_id}"
        
        return base_link + params

@public
def get_calendar_booking_link(business_name: Optional[str] = None, proposal_id: Optional[str] = None) -> Dict:
    """Get a calendar booking link for scheduling a strategy call."""
    calendar_service = CalendarService()
    
    if business_name and proposal_id:
        link = calendar_service.get_custom_booking_link(business_name, proposal_id)
    else:
        link = calendar_service.get_booking_link()
    
    return {
        "booking_link": link,
        "message": "Click the link to schedule your strategy call to discuss implementing your custom AI agent system."
    }

@public
def mark_calendar_booking_completed(session_id: str) -> Dict:
    """Mark that a user has completed calendar booking."""
    try:
        from core.chat_session import ChatSession
        import uuid
        
        session_uuid = uuid.UUID(session_id)
        
        ChatSession.sql(
            "UPDATE chat_sessions SET calendar_booking_completed = true WHERE id = %(session_id)s",
            {"session_id": session_uuid}
        )
        
        return {"success": True, "message": "Calendar booking marked as completed"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
