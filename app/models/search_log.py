"""
Search Log model for MongoDB
Tracks all user interactions, searches, and actions
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4


class SearchLog(BaseModel):
    """Search and activity log model"""
    telegram_id: int = Field(..., description="User's Telegram ID")
    event_type: str = Field(..., description="Type: command, button, search, action")
    query_text: Optional[str] = Field(None, description="User input or action description")
    module_name: Optional[str] = Field(None, description="Module name (m1_ai, m2_breach, etc.)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    session_id: str = Field(default_factory=lambda: str(uuid4()), description="Session identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    
    class Config:
        json_schema_extra = {
            "example": {
                "telegram_id": 123456789,
                "event_type": "search",
                "query_text": "check email breach",
                "module_name": "m2_breach",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "metadata": {
                    "email": "test@example.com",
                    "result": "found"
                },
                "ip_address": "192.168.1.1",
                "user_agent": "TelegramBot/1.0"
            }
        }


class SearchLogInDB(SearchLog):
    """Search log as stored in database"""
    pass
