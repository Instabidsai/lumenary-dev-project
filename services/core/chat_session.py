from solar import Table, ColumnDetails
from typing import Optional, Dict
from datetime import datetime
import uuid

class ChatSession(Table):
    __tablename__ = "chat_sessions"
    
    id: uuid.UUID = ColumnDetails(default_factory=uuid.uuid4, primary_key=True)
    business_name: Optional[str] = None
    industry: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    session_status: str = "active"  # active, completed, abandoned
    pain_points: Optional[Dict] = None  # JSON storage for identified pain points
    proposal_generated: bool = False
    google_drive_uploaded: bool = False
    calendar_booking_completed: bool = False
    created_at: datetime = ColumnDetails(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
