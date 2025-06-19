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
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
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
            # Get service account credentials from environment variable
            service_account_json = os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON")
            if not service_account_json:
                print("Warning: GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON not found in environment variables")
                return
            
            # Parse the JSON credentials
            credentials_info = json.loads(service_account_json)
            
            # Create credentials object
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            
            # Build the service
            self.service = build('drive', 'v3', credentials=credentials)
            print("Google Drive service initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize Google Drive service: {e}")
            self.service = None