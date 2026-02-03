"""
Job Model
Schema for job listings from various sources
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Job(BaseModel):
    """Job listing model"""
    
    title: str
    company: str
    location: str
    type: str = "onsite"  # "remote", "onsite", "hybrid"
    category: str = "general"  # "IT", "government", "internship", "general"
    salary: Optional[str] = None
    description: str
    url: str
    source: str  # "remotive", "sarkari_exam", etc.
    tags: List[str] = Field(default_factory=list)
    country: str = "global"  # "global", "india", "us", "uk"
    posted_at: Optional[datetime] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    hash: str  # For deduplication
    expires_at: Optional[datetime] = None  # TTL field
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class JobFilter(BaseModel):
    """Job filter criteria"""
    
    keyword: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    country: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    page: int = 1
    limit: int = 10
