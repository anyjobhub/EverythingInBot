"""
Telegram Mini App (TMA) API Endpoints
Backend API for the React-based Telegram Mini App
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.database import Database

router = APIRouter(prefix="/api/tma", tags=["Telegram Mini App"])


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class CourseResponse(BaseModel):
    """Course response model"""
    id: str
    title: str
    platform: str
    instructor: Optional[str]
    difficulty: str
    duration: Optional[str]
    category: str
    description: str
    url: str
    thumbnail: Optional[str]
    rating: Optional[float]


class JobResponse(BaseModel):
    """Job response model"""
    id: str
    title: str
    company: str
    location: str
    type: str
    category: str
    salary: Optional[str]
    description: str
    url: str
    tags: List[str]
    country: str


class UserProfile(BaseModel):
    """User profile model"""
    telegram_id: int
    username: Optional[str]
    join_date: datetime
    last_active: datetime
    total_searches: int
    total_commands: int
    modules_used: List[str]


# ============================================
# AUTHENTICATION
# ============================================

async def verify_telegram_webapp(
    x_telegram_init_data: Optional[str] = Header(None)
) -> int:
    """
    Verify Telegram WebApp init data
    
    Args:
        x_telegram_init_data: Telegram WebApp init data from header
        
    Returns:
        Telegram user ID
        
    Raises:
        HTTPException: If authentication fails
    """
    # In production, verify the init data hash
    # For now, simple validation
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Parse init data and extract user_id
    # Simplified for now - implement proper validation
    try:
        # Extract user_id from init data
        # Format: "user={"id":123456,...}&..."
        user_id = 123456  # Placeholder
        return user_id
    except:
        raise HTTPException(status_code=401, detail="Invalid init data")


# ============================================
# COURSES ENDPOINTS
# ============================================

@router.get("/courses", response_model=List[CourseResponse])
async def get_courses(
    category: Optional[str] = None,
    platform: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 10
):
    """
    Get courses with optional filters
    
    Args:
        category: Filter by category
        platform: Filter by platform
        difficulty: Filter by difficulty
        search: Search query
        page: Page number (1-indexed)
        limit: Items per page
        
    Returns:
        List of courses
    """
    db = Database.get_db()
    
    # Build query
    query = {}
    if category:
        query['category'] = category
    if platform:
        query['platform'] = platform
    if difficulty:
        query['difficulty'] = difficulty
    if search:
        query['$or'] = [
            {'title': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    
    # Fetch courses
    skip = (page - 1) * limit
    courses = await db.courses.find(query).sort('fetched_at', -1).skip(skip).limit(limit).to_list(length=limit)
    
    # Convert to response model
    return [
        CourseResponse(
            id=str(course['_id']),
            title=course.get('title', ''),
            platform=course.get('platform', ''),
            instructor=course.get('instructor'),
            difficulty=course.get('difficulty', 'beginner'),
            duration=course.get('duration'),
            category=course.get('category', ''),
            description=course.get('description', ''),
            url=course.get('url', ''),
            thumbnail=course.get('thumbnail'),
            rating=course.get('rating')
        )
        for course in courses
    ]


@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str):
    """
    Get course details by ID
    
    Args:
        course_id: Course ID
        
    Returns:
        Course details
    """
    from bson import ObjectId
    
    db = Database.get_db()
    course = await db.courses.find_one({'_id': ObjectId(course_id)})
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return CourseResponse(
        id=str(course['_id']),
        title=course.get('title', ''),
        platform=course.get('platform', ''),
        instructor=course.get('instructor'),
        difficulty=course.get('difficulty', 'beginner'),
        duration=course.get('duration'),
        category=course.get('category', ''),
        description=course.get('description', ''),
        url=course.get('url', ''),
        thumbnail=course.get('thumbnail'),
        rating=course.get('rating')
    )


# ============================================
# JOBS ENDPOINTS
# ============================================

@router.get("/jobs", response_model=List[JobResponse])
async def get_jobs(
    category: Optional[str] = None,
    country: Optional[str] = None,
    job_type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 10
):
    """
    Get jobs with optional filters
    
    Args:
        category: Filter by category
        country: Filter by country
        job_type: Filter by type (remote, onsite, hybrid)
        search: Search query
        page: Page number
        limit: Items per page
        
    Returns:
        List of jobs
    """
    db = Database.get_db()
    
    # Build query
    query = {}
    if category:
        query['category'] = category
    if country:
        query['country'] = country
    if job_type:
        query['type'] = job_type
    if search:
        query['$or'] = [
            {'title': {'$regex': search, '$options': 'i'}},
            {'company': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    
    # Fetch jobs
    skip = (page - 1) * limit
    jobs = await db.jobs.find(query).sort('fetched_at', -1).skip(skip).limit(limit).to_list(length=limit)
    
    # Convert to response model
    return [
        JobResponse(
            id=str(job['_id']),
            title=job.get('title', ''),
            company=job.get('company', ''),
            location=job.get('location', ''),
            type=job.get('type', 'onsite'),
            category=job.get('category', ''),
            salary=job.get('salary'),
            description=job.get('description', ''),
            url=job.get('url', ''),
            tags=job.get('tags', []),
            country=job.get('country', 'global')
        )
        for job in jobs
    ]


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """
    Get job details by ID
    
    Args:
        job_id: Job ID
        
    Returns:
        Job details
    """
    from bson import ObjectId
    
    db = Database.get_db()
    job = await db.jobs.find_one({'_id': ObjectId(job_id)})
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse(
        id=str(job['_id']),
        title=job.get('title', ''),
        company=job.get('company', ''),
        location=job.get('location', ''),
        type=job.get('type', 'onsite'),
        category=job.get('category', ''),
        salary=job.get('salary'),
        description=job.get('description', ''),
        url=job.get('url', ''),
        tags=job.get('tags', []),
        country=job.get('country', 'global')
    )


# ============================================
# USER ENDPOINTS
# ============================================

@router.get("/user/profile", response_model=UserProfile)
async def get_user_profile(user_id: int = Depends(verify_telegram_webapp)):
    """
    Get user profile
    
    Args:
        user_id: Telegram user ID from auth
        
    Returns:
        User profile
    """
    db = Database.get_db()
    user = await db.users.find_one({'telegram_id': user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfile(
        telegram_id=user['telegram_id'],
        username=user.get('username'),
        join_date=user.get('join_date', datetime.utcnow()),
        last_active=user.get('last_active', datetime.utcnow()),
        total_searches=user.get('total_searches', 0),
        total_commands=user.get('total_commands', 0),
        modules_used=user.get('modules_used', [])
    )


@router.get("/user/history")
async def get_user_history(
    user_id: int = Depends(verify_telegram_webapp),
    limit: int = 50
):
    """
    Get user search history
    
    Args:
        user_id: Telegram user ID from auth
        limit: Number of records to return
        
    Returns:
        User search history
    """
    db = Database.get_db()
    
    history = await db.search_logs.find(
        {'telegram_id': user_id}
    ).sort('timestamp', -1).limit(limit).to_list(length=limit)
    
    return [
        {
            'event_type': log.get('event_type'),
            'query_text': log.get('query_text'),
            'module_name': log.get('module_name'),
            'timestamp': log.get('timestamp')
        }
        for log in history
    ]


@router.get("/stats")
async def get_platform_stats():
    """
    Get platform statistics
    
    Returns:
        Platform stats
    """
    db = Database.get_db()
    
    total_users = await db.users.count_documents({})
    total_jobs = await db.jobs.count_documents({})
    total_courses = await db.courses.count_documents({})
    total_searches = await db.search_logs.count_documents({})
    
    return {
        'total_users': total_users,
        'total_jobs': total_jobs,
        'total_courses': total_courses,
        'total_searches': total_searches
    }
