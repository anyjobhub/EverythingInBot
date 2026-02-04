"""
Search Log model for MongoDB
Tracks all user interactions, searches, and actions
Enhanced with ephemeral mode (auto-delete after 5 minutes)
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4


class SearchLog(BaseModel):
    """Search and activity log model with ephemeral support"""
    telegram_id: int = Field(..., description="User's Telegram ID")
    username: Optional[str] = Field(None, description="User's username")
    event_type: str = Field(..., description="Type: command, button, search, action")
    query_text: Optional[str] = Field(None, description="User input or action description")
    module_name: Optional[str] = Field(None, description="Module name (m1_ai, m2_breach, etc.)")
    
    # Ephemeral mode fields
    result_message_id: Optional[int] = Field(None, description="Message ID of search result")
    chat_id: Optional[int] = Field(None, description="Chat ID where result was sent")
    expires_at: Optional[datetime] = Field(None, description="When result expires (for auto-delete)")
    is_admin: bool = Field(False, description="Admin messages don't auto-delete")
    deleted: bool = Field(False, description="Whether message was deleted")
    deleted_at: Optional[datetime] = Field(None, description="When message was deleted")
    
    # Tracking fields
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    session_id: str = Field(default_factory=lambda: str(uuid4()), description="Session identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    
    class Config:
        json_schema_extra = {
            "example": {
                "telegram_id": 123456789,
                "username": "john_doe",
                "event_type": "search",
                "query_text": "python jobs",
                "module_name": "m4_jobs",
                "result_message_id": 987654321,
                "chat_id": 123456789,
                "expires_at": "2026-02-04T16:17:57Z",
                "is_admin": False,
                "deleted": False,
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "metadata": {
                    "results_count": 10,
                    "search_type": "jobs"
                },
                "ip_address": "192.168.1.1",
                "user_agent": "TelegramBot/1.0"
            }
        }
    
    @classmethod
    def create_ephemeral(
        cls,
        telegram_id: int,
        query_text: str,
        result_message_id: int,
        chat_id: int,
        module_name: str,
        username: Optional[str] = None,
        is_admin: bool = False,
        expiry_seconds: int = 300,
        **kwargs
    ) -> "SearchLog":
        """
        Create an ephemeral search log (auto-deletes after expiry)
        
        Args:
            telegram_id: User's Telegram ID
            query_text: Search query
            result_message_id: Message ID to delete
            chat_id: Chat ID
            module_name: Module name
            username: User's username
            is_admin: Admin flag (admins don't auto-delete)
            expiry_seconds: Seconds until expiry (default: 300 = 5 min)
            **kwargs: Additional metadata
        
        Returns:
            SearchLog instance
        """
        now = datetime.utcnow()
        
        return cls(
            telegram_id=telegram_id,
            username=username,
            event_type="search",
            query_text=query_text,
            module_name=module_name,
            result_message_id=result_message_id,
            chat_id=chat_id,
            expires_at=now + timedelta(seconds=expiry_seconds),
            is_admin=is_admin,
            deleted=False,
            timestamp=now,
            metadata=kwargs
        )
    
    def is_expired(self) -> bool:
        """Check if this search result has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def should_auto_delete(self) -> bool:
        """
        Check if this message should be auto-deleted
        Admin messages are never auto-deleted
        """
        return (
            not self.is_admin 
            and not self.deleted 
            and self.result_message_id is not None
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB insertion"""
        return self.model_dump(exclude_none=True)


class SearchLogInDB(SearchLog):
    """Search log as stored in database"""
    pass
