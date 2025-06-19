from solar import Table, ColumnDetails
from typing import Optional
from datetime import datetime
import uuid

class ChatMessage(Table):
    __tablename__ = "chat_messages"
    
    id: uuid.UUID = ColumnDetails(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID  # References chat_sessions.id
    role: str  # "user" or "assistant"
    content: str
    message_order: int  # For maintaining conversation order
    created_at: datetime = ColumnDetails(default_factory=datetime.now)
