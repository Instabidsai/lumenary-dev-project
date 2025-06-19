from typing import List, Dict, Optional, Tuple
from openai import OpenAI
import os
import json
from core.chat_session import ChatSession
from core.chat_message import ChatMessage
from core.business_profile import BusinessProfile
from solar.access import public
import uuid

class ConversationEngine:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
    
    def get_initial_question(self) -> str:
        """Get the first question to start the conversation."""
        return "Hi! I'm here to help you discover how AI agents could transform your business operations. Let's start with the basics - what's your business name and what industry are you in?"
    
    def determine_next_question(self, session_id: uuid.UUID, conversation_history: List[Dict]) -> str:
        """Determine the next question based on conversation history."""
        
        # Get conversation context
        context = self._build_conversation_context(conversation_history)
        
        system_prompt = """You are a business scoping agent that helps identify operational pain points and automation opportunities. 

Your goal is to ask intelligent follow-up questions that will help you understand:
1. The business's main operational challenges
2. Time-wasting manual tasks
3. Customer service bottlenecks
4. Communication inefficiencies
5. Data management issues
6. Scheduling and workflow problems

Ask ONE focused question at a time. Make questions conversational and specific based on what the user has already shared. Don't ask generic questions - build on their previous responses.

Examples of good follow-up questions:
- "You mentioned handling customer emails takes a lot of time. About how many emails do you process daily, and what types of questions come up most often?"
- "Since you're in retail, what's your biggest challenge during busy seasons - is it inventory tracking, customer inquiries, or something else?"
- "That scheduling conflict issue sounds frustrating. What usually causes these conflicts - double bookings, last-minute changes, or communication gaps?"

Keep questions natural and empathetic. Show that you understand their pain points."""

        response = self.client.chat.completions.create(
            model="openai/o4-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Conversation so far:\n{context}\n\nWhat should I ask next to better understand their business challenges?"}
            ]
        )
        
        return response.choices[0].message.content.strip()
    
    def _build_conversation_context(self, conversation_history: List[Dict]) -> str:
        """Build context string from conversation history."""
        context_parts = []
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            role = "Business Owner" if msg["role"] == "user" else "Agent"
            context_parts.append(f"{role}: {msg['content']}")
        return "\n".join(context_parts)
    
    def should_generate_proposal(self, conversation_history: List[Dict]) -> bool:
        """Determine if enough information has been gathered to generate a proposal."""
        user_messages = [msg for msg in conversation_history if msg["role"] == "user"]
        
        # Need at least 4 substantial user responses
        if len(user_messages) < 4:
            return False
        
        # Check if we have enough depth of information
        system_prompt = """Analyze this business conversation to determine if we have enough information to create a meaningful agent system proposal.

We need to understand:
1. Business type and industry
2. Main operational challenges or pain points
3. Time-wasting manual processes
4. Customer interaction challenges
5. Specific bottlenecks or inefficiencies

Return "ready" if we have sufficient detail in at least 3 of these areas. Return "need_more" if we need additional information."""

        context = self._build_conversation_context(conversation_history)
        
        response = self.client.chat.completions.create(
            model="openai/o4-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Conversation:\n{context}\n\nDo we have enough information to generate a proposal?"}
            ]
        )
        
        return "ready" in response.choices[0].message.content.lower()

@public
def start_chat_session() -> Dict:
    """Start a new chat session."""
    session = ChatSession()
    session.sync()
    
    engine = ConversationEngine()
    initial_question = engine.get_initial_question()
    
    # Save the initial agent message
    message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=initial_question,
        message_order=1
    )
    message.sync()
    
    return {
        "session_id": str(session.id),
        "message": initial_question
    }

@public
def send_chat_message(session_id: str, user_message: str) -> Dict:
    """Process a user message and return the agent's response."""
    session_uuid = uuid.UUID(session_id)
    
    # Get conversation history
    history_results = ChatMessage.sql(
        "SELECT role, content FROM chat_messages WHERE session_id = %(session_id)s ORDER BY message_order",
        {"session_id": session_uuid}
    )
    conversation_history = [{"role": row["role"], "content": row["content"]} for row in history_results]
    
    # Get next message order
    order_result = ChatMessage.sql(
        "SELECT COALESCE(MAX(message_order), 0) + 1 as next_order FROM chat_messages WHERE session_id = %(session_id)s",
        {"session_id": session_uuid}
    )
    next_order = order_result[0]["next_order"]
    
    # Save user message
    user_msg = ChatMessage(
        session_id=session_uuid,
        role="user",
        content=user_message,
        message_order=next_order
    )
    user_msg.sync()
    
    # Add user message to history for processing
    conversation_history.append({"role": "user", "content": user_message})
    
    engine = ConversationEngine()
    
    # Check if ready for proposal generation
    if engine.should_generate_proposal(conversation_history):
        return {
            "message": "Thank you for sharing all that information! I have a clear picture of your business challenges. Let me analyze everything and create a custom agent system recommendation for you. This will just take a moment...",
            "ready_for_proposal": True
        }
    
    # Generate next question
    agent_response = engine.determine_next_question(session_uuid, conversation_history)
    
    # Save agent response
    agent_msg = ChatMessage(
        session_id=session_uuid,
        role="assistant",
        content=agent_response,
        message_order=next_order + 1
    )
    agent_msg.sync()
    
    return {
        "message": agent_response,
        "ready_for_proposal": False
    }

@public
def get_chat_history(session_id: str) -> List[Dict]:
    """Get the chat history for a session."""
    session_uuid = uuid.UUID(session_id)
    
    messages = ChatMessage.sql(
        "SELECT role, content, created_at FROM chat_messages WHERE session_id = %(session_id)s ORDER BY message_order",
        {"session_id": session_uuid}
    )
    
    return [
        {
            "role": msg["role"],
            "content": msg["content"],
            "timestamp": msg["created_at"].isoformat()
        }
        for msg in messages
    ]
