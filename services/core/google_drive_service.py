import os
import json
from typing import Optional, Dict
from datetime import datetime
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Google API packages not available. Install google-api-python-client and google-auth to enable Google Drive integration.")
from io import BytesIO
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocDocument, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not available. Install reportlab to enable PDF generation.")
from core.proposal_recommendation import ProposalRecommendation
from core.business_profile import BusinessProfile
from core.chat_session import ChatSession
from solar.access import public
import uuid

class GoogleDriveService:
    def __init__(self):
        self.service = None
        if GOOGLE_AVAILABLE:
            self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Drive service with service account credentials."""
        try:
            service_account_json = os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON")
            if not service_account_json:
                print("Warning: GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON not found in environment variables")
                return
            
            credentials_info = json.loads(service_account_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            
            self.service = build('drive', 'v3', credentials=credentials)
            print("Google Drive service initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize Google Drive service: {e}")
            self.service = None
    
    def _create_folder_if_not_exists(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Optional[str]:
        """Create a folder if it doesn't exist and return its ID."""
        if not self.service:
            return None
        
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            else:
                query += " and 'root' in parents"
            
            results = self.service.files().list(q=query).execute()
            items = results.get('files', [])
            
            if items:
                return items[0]['id']
            
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(body=folder_metadata).execute()
            return folder.get('id')
            
        except Exception as e:
            print(f"Error creating/finding folder {folder_name}: {e}")
            return None
    
    def _ensure_folder_structure(self) -> Optional[str]:
        """Ensure the AgentsMadeEasy/ScopingResults folder structure exists."""
        main_folder_id = self._create_folder_if_not_exists("AgentsMadeEasy")
        if not main_folder_id:
            return None
        
        scoping_folder_id = self._create_folder_if_not_exists("ScopingResults", main_folder_id)
        return scoping_folder_id
    
    def upload_proposal(self, proposal_id: str) -> Dict:
        """Upload a proposal to Google Drive and return upload status."""
        if not GOOGLE_AVAILABLE:
            return {"success": False, "error": "Google Drive integration not available - missing required packages"}
        
        try:
            proposal_uuid = uuid.UUID(proposal_id)
            
            proposal_results = ProposalRecommendation.sql(
                """SELECT pr.*, bp.business_name, bp.industry 
                   FROM proposal_recommendations pr
                   JOIN business_profiles bp ON pr.business_profile_id = bp.id
                   WHERE pr.id = %(proposal_id)s""",
                {"proposal_id": proposal_uuid}
            )
            
            if not proposal_results:
                return {"success": False, "error": "Proposal not found"}
            
            proposal_data = proposal_results[0]
            
            if not self.service:
                return {"success": False, "error": "Google Drive service not available - check credentials"}
            
            folder_id = self._ensure_folder_structure()
            if not folder_id:
                return {"success": False, "error": "Failed to create/access Google Drive folders"}
            
            # Generate simple text file
            content = f"""Custom AI Agent System Proposal

Business: {proposal_data.get('business_name', 'N/A')}
Industry: {proposal_data.get('industry', 'N/A')}
Pricing Tier: {proposal_data.get('pricing_tier', 'N/A').title()}
Estimated Cost: {proposal_data.get('estimated_cost', 'N/A')}

Executive Summary:
{proposal_data.get('proposal_summary', '')}

Recommended Agents:
{chr(10).join([f"- {agent.get('name', '')}: {agent.get('purpose', '')}" for agent in proposal_data.get('recommended_agents', [])])}

Key Benefits:
{chr(10).join([f"- {benefit}" for benefit in proposal_data.get('key_benefits', [])])}

Implementation Timeline: {proposal_data.get('implementation_timeline', 'To be determined')}

Full Proposal:
{proposal_data.get('full_proposal_content', '')}

Generated by Agents Made Easy - Business Scoping Agent
Date: {datetime.now().strftime('%B %d, %Y')}
"""
            
            buffer = BytesIO()
            buffer.write(content.encode('utf-8'))
            buffer.seek(0)
            
            business_name = proposal_data['business_name'].replace(' ', '_').replace('/', '_')
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"AgentProposal_{business_name}_{date_str}.txt"
            
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            media = MediaIoBaseUpload(buffer, mimetype='text/plain', resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            
            ProposalRecommendation.sql(
                "UPDATE proposal_recommendations SET google_drive_file_id = %(file_id)s, pdf_generated = true WHERE id = %(proposal_id)s",
                {"file_id": file_id, "proposal_id": proposal_uuid}
            )
            
            ChatSession.sql(
                "UPDATE chat_sessions SET google_drive_uploaded = true WHERE id = %(session_id)s",
                {"session_id": proposal_data['session_id']}
            )
            
            return {
                "success": True,
                "file_id": file_id,
                "filename": filename,
                "message": f"Proposal successfully uploaded to Google Drive as {filename}"
            }
            
        except Exception as e:
            print(f"Error uploading to Google Drive: {e}")
            return {"success": False, "error": f"Upload failed: {str(e)}"}

@public
def upload_proposal_to_drive(proposal_id: str) -> Dict:
    """Public endpoint to upload a proposal to Google Drive."""
    drive_service = GoogleDriveService()
    return drive_service.upload_proposal(proposal_id)

@public
def test_google_drive_connection() -> Dict:
    """Test Google Drive service connection."""
    if not GOOGLE_AVAILABLE:
        return {
            "connected": False,
            "message": "Google Drive packages not installed. Install google-api-python-client and google-auth to enable Google Drive integration."
        }
    
    drive_service = GoogleDriveService()
    
    if not drive_service.service:
        return {
            "connected": False,
            "message": "Google Drive service not initialized. Check GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON environment variable."
        }
    
    try:
        results = drive_service.service.files().list(pageSize=1).execute()
        return {
            "connected": True,
            "message": "Google Drive connection successful"
        }
    except Exception as e:
        return {
            "connected": False,
            "message": f"Google Drive connection failed: {str(e)}"
        }