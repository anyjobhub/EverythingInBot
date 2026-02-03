"""
Data Normalization Utilities
Standardize data from different sources into unified schemas
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import re


def normalize_job_data(
    raw_data: Dict[str, Any],
    source: str,
    default_country: str = "global"
) -> Dict[str, Any]:
    """
    Normalize job data from various sources
    
    Args:
        raw_data: Raw job data from source
        source: Source identifier
        default_country: Default country if not specified
        
    Returns:
        Normalized job dictionary
    """
    # Extract common fields with fallbacks
    title = raw_data.get('title') or raw_data.get('job_title') or raw_data.get('position', 'Untitled')
    company = raw_data.get('company') or raw_data.get('company_name') or raw_data.get('employer', 'Unknown')
    location = raw_data.get('location') or raw_data.get('job_location') or 'Not specified'
    description = raw_data.get('description') or raw_data.get('job_description') or ''
    url = raw_data.get('url') or raw_data.get('link') or raw_data.get('apply_url', '')
    
    # Determine job type
    job_type = determine_job_type(title, description, location)
    
    # Determine category
    category = determine_job_category(title, description, source)
    
    # Extract salary if available
    salary = extract_salary(raw_data.get('salary') or raw_data.get('salary_range'))
    
    # Extract tags
    tags = extract_tags(raw_data.get('tags') or raw_data.get('skills') or [])
    
    # Parse posted date
    posted_at = parse_date(raw_data.get('posted_at') or raw_data.get('publication_date'))
    
    # Set expiration (24 hours from now)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    return {
        'title': clean_text(title),
        'company': clean_text(company),
        'location': clean_text(location),
        'type': job_type,
        'category': category,
        'salary': salary,
        'description': clean_text(description[:500]),  # Limit description
        'url': url,
        'source': source,
        'tags': tags,
        'country': default_country,
        'posted_at': posted_at,
        'fetched_at': datetime.utcnow(),
        'expires_at': expires_at
    }


def normalize_course_data(
    raw_data: Dict[str, Any],
    source: str
) -> Dict[str, Any]:
    """
    Normalize course data from various platforms
    
    Args:
        raw_data: Raw course data from source
        source: Source identifier
        
    Returns:
        Normalized course dictionary
    """
    # Extract common fields
    title = raw_data.get('title') or raw_data.get('name') or 'Untitled Course'
    platform = raw_data.get('platform') or source
    instructor = raw_data.get('instructor') or raw_data.get('author') or raw_data.get('instructors')
    description = raw_data.get('description') or raw_data.get('summary') or ''
    url = raw_data.get('url') or raw_data.get('link') or ''
    
    # Determine difficulty
    difficulty = determine_difficulty(raw_data.get('difficulty') or raw_data.get('level'))
    
    # Determine category
    category = determine_course_category(title, description, raw_data.get('category'))
    
    # Extract duration
    duration = extract_duration(raw_data.get('duration') or raw_data.get('length'))
    
    # Extract other fields
    thumbnail = raw_data.get('thumbnail') or raw_data.get('image')
    rating = extract_rating(raw_data.get('rating'))
    language = raw_data.get('language') or 'en'
    
    # Set expiration (48 hours from now)
    expires_at = datetime.utcnow() + timedelta(hours=48)
    
    return {
        'title': clean_text(title),
        'platform': platform.lower(),
        'instructor': clean_text(instructor) if instructor else None,
        'difficulty': difficulty,
        'duration': duration,
        'category': category,
        'description': clean_text(description[:500]),
        'url': url,
        'thumbnail': thumbnail,
        'rating': rating,
        'language': language,
        'source': source,
        'fetched_at': datetime.utcnow(),
        'expires_at': expires_at
    }


# Helper functions

def clean_text(text: str) -> str:
    """Remove extra whitespace and HTML tags"""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', str(text))
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()


def determine_job_type(title: str, description: str, location: str) -> str:
    """Determine if job is remote, onsite, or hybrid"""
    text = f"{title} {description} {location}".lower()
    
    if any(word in text for word in ['remote', 'work from home', 'wfh', 'anywhere']):
        return 'remote'
    elif 'hybrid' in text:
        return 'hybrid'
    else:
        return 'onsite'


def determine_job_category(title: str, description: str, source: str) -> str:
    """Determine job category"""
    text = f"{title} {description}".lower()
    
    # Check source first
    if 'sarkari' in source or 'govt' in source or 'government' in source:
        return 'government'
    
    if 'intern' in text:
        return 'internship'
    
    # Check for IT/Software
    it_keywords = ['software', 'developer', 'engineer', 'programmer', 'python', 'java', 'devops', 'data']
    if any(keyword in text for keyword in it_keywords):
        return 'IT'
    
    return 'general'


def determine_course_category(title: str, description: str, raw_category: Optional[str]) -> str:
    """Determine course category"""
    text = f"{title} {description}".lower()
    
    # Use raw category if available
    if raw_category:
        raw_category = raw_category.lower()
        if 'python' in raw_category:
            return 'python'
        elif 'security' in raw_category or 'cyber' in raw_category:
            return 'cybersecurity'
        elif 'ai' in raw_category or 'machine learning' in raw_category:
            return 'ai'
        elif 'web' in raw_category:
            return 'web_development'
    
    # Analyze text
    if 'python' in text:
        return 'python'
    elif 'security' in text or 'hacking' in text or 'cyber' in text:
        return 'cybersecurity'
    elif 'ai' in text or 'machine learning' in text or 'ml' in text:
        return 'ai'
    elif 'web development' in text or 'html' in text or 'css' in text or 'javascript' in text:
        return 'web_development'
    elif 'cloud' in text or 'aws' in text or 'azure' in text or 'devops' in text:
        return 'cloud'
    elif 'data science' in text or 'data analysis' in text:
        return 'data_science'
    elif 'mobile' in text or 'android' in text or 'ios' in text or 'flutter' in text:
        return 'mobile'
    
    return 'general'


def determine_difficulty(raw_difficulty: Optional[str]) -> str:
    """Normalize difficulty level"""
    if not raw_difficulty:
        return 'beginner'
    
    raw_difficulty = raw_difficulty.lower()
    
    if 'beginner' in raw_difficulty or 'intro' in raw_difficulty or 'basic' in raw_difficulty:
        return 'beginner'
    elif 'advanced' in raw_difficulty or 'expert' in raw_difficulty:
        return 'advanced'
    elif 'intermediate' in raw_difficulty or 'medium' in raw_difficulty:
        return 'intermediate'
    
    return 'beginner'


def extract_salary(salary_str: Optional[str]) -> Optional[str]:
    """Extract and normalize salary information"""
    if not salary_str:
        return None
    
    # Clean and return
    salary_str = clean_text(str(salary_str))
    return salary_str if salary_str else None


def extract_tags(tags: Any) -> list:
    """Extract and normalize tags"""
    if isinstance(tags, list):
        return [clean_text(tag) for tag in tags if tag][:10]  # Limit to 10 tags
    elif isinstance(tags, str):
        return [clean_text(tag) for tag in tags.split(',') if tag][:10]
    return []


def extract_duration(duration: Optional[str]) -> Optional[str]:
    """Extract and normalize duration"""
    if not duration:
        return None
    
    duration = clean_text(str(duration))
    return duration if duration else None


def extract_rating(rating: Any) -> Optional[float]:
    """Extract and normalize rating"""
    if rating is None:
        return None
    
    try:
        rating_float = float(rating)
        # Clamp between 0 and 5
        return max(0.0, min(5.0, rating_float))
    except (ValueError, TypeError):
        return None


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime"""
    if not date_str:
        return None
    
    try:
        # Try ISO format first
        return datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
    except:
        try:
            # Try common formats
            from dateutil import parser
            return parser.parse(str(date_str))
        except:
            return None
