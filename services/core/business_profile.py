from solar import Table, ColumnDetails
from typing import Optional, List, Dict
from datetime import datetime
import uuid

class BusinessProfile(Table):
    __tablename__ = "business_profiles"
    
    id: uuid.UUID = ColumnDetails(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID  # References chat_sessions.id
    business_name: str
    industry: str
    business_size: Optional[str] = None  # "small", "medium", "large"
    main_pain_points: List[str]  # Array of identified pain points
    time_wasters: List[str]  # Array of time-wasting activities
    bottlenecks: List[str]  # Array of operational bottlenecks
    automation_opportunities: List[str]  # Array of automation possibilities
    customer_service_challenges: List[str]  # Array of customer service issues
    additional_context: Optional[Dict] = None  # Additional structured data
    created_at: datetime = ColumnDetails(default_factory=datetime.now)
