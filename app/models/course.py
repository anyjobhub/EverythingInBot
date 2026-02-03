"""
Course Model
Schema for course listings from various platforms
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Course(BaseModel):
    """Course model"""
    
    title: str
    platform: str  # "udemy", "coursera", "edx", etc.
    instructor: Optional[str] = None
    difficulty: str = "beginner"  # "beginner", "intermediate", "advanced"
    duration: Optional[str] = None  # "4 hours", "6 weeks"
    category: str  # "python", "cybersecurity", "ai", etc.
    description: str
    url: str
    thumbnail: Optional[str] = None
    rating: Optional[float] = None
    language: str = "en"
    source: str  # "classcentral", "udemy_api", etc.
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    hash: str  # For deduplication
    expires_at: Optional[datetime] = None  # TTL field
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CourseFilter(BaseModel):
    """Course filter criteria"""
    
    category: Optional[str] = None
    platform: Optional[str] = None
    difficulty: Optional[str] = None
    language: Optional[str] = None
    keyword: Optional[str] = None
    page: int = 1
    limit: int = 10
