from solar import Table, ColumnDetails
from typing import Optional, List, Dict
from datetime import datetime
import uuid

class ProposalRecommendation(Table):
    __tablename__ = "proposal_recommendations"
    
    id: uuid.UUID = ColumnDetails(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID  # References chat_sessions.id
    business_profile_id: uuid.UUID  # References business_profiles.id
    pricing_tier: str  # "starter" or "pro"
    recommended_agents: List[Dict]  # Array of recommended agent configurations
    implementation_timeline: str
    estimated_cost: Optional[str] = None
    key_benefits: List[str]  # Array of expected benefits
    technical_requirements: List[str]  # Array of technical needs
    integration_points: List[str]  # Array of required integrations
    proposal_summary: str  # Executive summary of the proposal
    full_proposal_content: str  # Complete proposal text
    google_drive_file_id: Optional[str] = None  # Google Drive file ID when uploaded
    pdf_generated: bool = False
    created_at: datetime = ColumnDetails(default_factory=datetime.now)
