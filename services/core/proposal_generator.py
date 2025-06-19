from typing import List, Dict, Optional, Tuple
from openai import OpenAI
import os
import json
from datetime import datetime
from core.chat_session import ChatSession
from core.chat_message import ChatMessage
from core.business_profile import BusinessProfile
from core.proposal_recommendation import ProposalRecommendation
from solar.access import public
import uuid

class ProposalGenerator:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
    
    def extract_business_profile(self, conversation_history: List[Dict]) -> Dict:
        """Extract structured business information from conversation."""
        
        context = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        
        system_prompt = """Extract structured business information from this conversation. 
        Focus on identifying specific pain points, time wasters, bottlenecks, and automation opportunities mentioned by the business owner."""
        
        schema = {
            "name": "business_profile",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "business_name": {"type": "string", "description": "Name of the business"},
                    "industry": {"type": "string", "description": "Industry or business type"},
                    "business_size": {"type": ["string", "null"], "description": "Small, medium, or large business"},
                    "main_pain_points": {
                        "type": "array",
                        "description": "Primary operational challenges",
                        "items": {"type": "string"}
                    },
                    "time_wasters": {
                        "type": "array", 
                        "description": "Manual tasks that waste time",
                        "items": {"type": "string"}
                    },
                    "bottlenecks": {
                        "type": "array",
                        "description": "Operational bottlenecks and inefficiencies", 
                        "items": {"type": "string"}
                    },
                    "automation_opportunities": {
                        "type": "array",
                        "description": "Tasks that could be automated",
                        "items": {"type": "string"}
                    },
                    "customer_service_challenges": {
                        "type": "array",
                        "description": "Customer interaction and service issues",
                        "items": {"type": "string"}
                    }
                },
                "required": ["business_name", "industry", "business_size", "main_pain_points", "time_wasters", "bottlenecks", "automation_opportunities", "customer_service_challenges"],
                "additionalProperties": False
            }
        }
        
        response = self.client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            response_format={"type": "json_schema", "json_schema": schema}
        )
        
        return json.loads(response.choices[0].message.content)