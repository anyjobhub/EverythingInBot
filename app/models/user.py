"""
User Model (Pydantic)
MongoDB document schema for users
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class UserModel(BaseModel):
    """User document model with comprehensive tracking"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    telegram_id: int = Field(..., description="Telegram user ID")
    username: Optional[str] = Field(None, description="Telegram username")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    language_code: Optional[str] = Field("en", description="User's language code")
    
    # Subscription
    tier: Literal["guest", "free", "pro"] = Field(default="free", description="Subscription tier")
    
    # Usage tracking
    total_requests: int = Field(default=0, description="Total API requests")
    daily_requests: int = Field(default=0, description="Requests today")
    last_request_date: Optional[datetime] = Field(None, description="Last request date")
    
    # New tracking fields for logging system
    join_date: datetime = Field(default_factory=datetime.utcnow, description="First interaction timestamp")
    total_searches: int = Field(default=0, description="Total searches performed")
    total_commands: int = Field(default=0, description="Total commands executed")
    modules_used: List[str] = Field(default_factory=list, description="List of modules used")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    
    # Preferences
    language: str = Field(default="en", description="User language")
    notifications_enabled: bool = Field(default=True)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserCreate(BaseModel):
    """User creation schema"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdate(BaseModel):
    """User update schema"""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    tier: Optional[Literal["guest", "free", "pro"]] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
