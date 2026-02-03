"""
Course Fetcher
Automated course fetching from 6 public platforms
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional

from app.fetchers.utils import fetch_json, fetch_rss
from app.utils.normalization import normalize_course_data
from app.utils.deduplication import generate_course_hash

logger = logging.getLogger(__name__)


# ============================================
# COURSE SOURCES
# ============================================

async def fetch_classcentral() -> List[Dict[str, Any]]:
    """
    Fetch courses from ClassCentral RSS
    URL: https://www.classcentral.com/report/feed/
    """
    logger.info("Fetching courses from ClassCentral...")
    
    url = "https://www.classcentral.com/report/feed/"
    entries = await fetch_rss(url)
    
    if not entries:
        logger.warning("No courses found from ClassCentral")
        return []
    
    courses = []
    for entry in entries[:30]:
        try:
            # Extract course info from RSS entry
            title = entry.get('title', '')
            
            # Filter for course-related content
            if not any(word in title.lower() for word in ['course', 'learn', 'tutorial', 'class', 'training']):
                continue
            
            normalized = normalize_course_data(
                {
                    'title': title,
                    'platform': 'classcentral',
                    'description': entry.get('summary', '')[:500],
                    'url': entry.get('link'),
                    'category': 'general'
                },
                source='classcentral'
            )
            
            normalized['hash'] = generate_course_hash(
                normalized['title'],
                normalized['platform']
            )
            
            courses.append(normalized)
        except Exception as e:
            logger.error(f"Error normalizing ClassCentral course: {e}")
    
    logger.info(f"Fetched {len(courses)} courses from ClassCentral")
    return courses


async def fetch_udemy() -> List[Dict[str, Any]]:
    """
    Fetch free courses from Udemy API
    URL: https://www.udemy.com/api-2.0/courses/?price=price-free&language=en
    Note: May require API key in production
    """
    logger.info("Fetching courses from Udemy...")
    
    # Udemy API requires authentication
    # For now, return empty or use public course search
    # In production, use Udemy Affiliate API with proper credentials
    
    logger.warning("Udemy API requires authentication - skipping for now")
    return []
    
    # Example implementation with API key:
    # api_key = os.getenv('UDEMY_API_KEY')
    # if not api_key:
    #     return []
    # 
    # url = "https://www.udemy.com/api-2.0/courses/"
    # params = {
    #     'price': 'price-free',
    #     'language': 'en',
    #     'page_size': 50
    # }
    # headers = {
    #     'Authorization': f'Bearer {api_key}'
    # }
    # 
    # data = await fetch_json(url, headers=headers, params=params)
    # ...


async def fetch_coursera() -> List[Dict[str, Any]]:
    """
    Fetch courses from Coursera API
    URL: https://www.coursera.org/api/courses.v1
    """
    logger.info("Fetching courses from Coursera...")
    
    url = "https://www.coursera.org/api/courses.v1"
    params = {
        'fields': 'name,description,workload,photoUrl,instructors',
        'limit': 50
    }
    
    data = await fetch_json(url, params=params)
    
    if not data or 'elements' not in data:
        logger.warning("No courses found from Coursera")
        return []
    
    courses = []
    for course in data['elements']:
        try:
            # Extract instructor names
            instructors = course.get('instructors', [])
            instructor_name = instructors[0].get('fullName') if instructors else None
            
            normalized = normalize_course_data(
                {
                    'title': course.get('name'),
                    'platform': 'coursera',
                    'instructor': instructor_name,
                    'description': course.get('description', '')[:500],
                    'url': f"https://www.coursera.org/learn/{course.get('slug', '')}",
                    'thumbnail': course.get('photoUrl'),
                    'duration': course.get('workload'),
                    'category': 'general'
                },
                source='coursera'
            )
            
            normalized['hash'] = generate_course_hash(
                normalized['title'],
                normalized['platform']
            )
            
            courses.append(normalized)
        except Exception as e:
            logger.error(f"Error normalizing Coursera course: {e}")
    
    logger.info(f"Fetched {len(courses)} courses from Coursera")
    return courses


async def fetch_edx() -> List[Dict[str, Any]]:
    """
    Fetch courses from edX API
    URL: https://www.edx.org/api/catalog/v2/courses
    """
    logger.info("Fetching courses from edX...")
    
    url = "https://www.edx.org/api/catalog/v2/courses"
    params = {
        'limit': 50
    }
    
    data = await fetch_json(url, params=params)
    
    if not data or 'results' not in data:
        logger.warning("No courses found from edX")
        return []
    
    courses = []
    for course in data['results']:
        try:
            # Extract course details
            course_runs = course.get('course_runs', [])
            first_run = course_runs[0] if course_runs else {}
            
            normalized = normalize_course_data(
                {
                    'title': course.get('title'),
                    'platform': 'edx',
                    'instructor': first_run.get('staff', [{}])[0].get('name') if first_run.get('staff') else None,
                    'description': course.get('short_description', '')[:500],
                    'url': course.get('marketing_url', ''),
                    'thumbnail': course.get('image', {}).get('src'),
                    'difficulty': first_run.get('level_type'),
                    'category': 'general'
                },
                source='edx'
            )
            
            normalized['hash'] = generate_course_hash(
                normalized['title'],
                normalized['platform']
            )
            
            courses.append(normalized)
        except Exception as e:
            logger.error(f"Error normalizing edX course: {e}")
    
    logger.info(f"Fetched {len(courses)} courses from edX")
    return courses


async def fetch_freecodecamp() -> List[Dict[str, Any]]:
    """
    Fetch courses from freeCodeCamp RSS
    URL: https://www.freecodecamp.org/news/rss/
    """
    logger.info("Fetching courses from freeCodeCamp...")
    
    url = "https://www.freecodecamp.org/news/rss/"
    entries = await fetch_rss(url)
    
    if not entries:
        logger.warning("No courses found from freeCodeCamp")
        return []
    
    courses = []
    for entry in entries[:30]:
        try:
            title = entry.get('title', '')
            
            # Filter for tutorial/course content
            if not any(word in title.lower() for word in ['course', 'tutorial', 'learn', 'guide', 'bootcamp']):
                continue
            
            normalized = normalize_course_data(
                {
                    'title': title,
                    'platform': 'freecodecamp',
                    'instructor': entry.get('author', 'freeCodeCamp'),
                    'description': entry.get('summary', '')[:500],
                    'url': entry.get('link'),
                    'category': 'general'
                },
                source='freecodecamp'
            )
            
            normalized['hash'] = generate_course_hash(
                normalized['title'],
                normalized['platform']
            )
            
            courses.append(normalized)
        except Exception as e:
            logger.error(f"Error normalizing freeCodeCamp course: {e}")
    
    logger.info(f"Fetched {len(courses)} courses from freeCodeCamp")
    return courses


async def fetch_youtube_playlists() -> List[Dict[str, Any]]:
    """
    Fetch course playlists from YouTube Data API
    Channels: freeCodeCamp, Telusko, Programming with Mosh
    """
    logger.info("Fetching course playlists from YouTube...")
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        logger.warning("YouTube API key not found - skipping")
        return []
    
    # Search queries for course playlists
    queries = [
        "python full course",
        "web development bootcamp",
        "cybersecurity tutorial",
        "machine learning course",
        "data science tutorial"
    ]
    
    courses = []
    
    for query in queries:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'playlist',
            'maxResults': 5,
            'key': api_key,
            'videoDuration': 'long',  # Long videos (likely courses)
            'relevanceLanguage': 'en'
        }
        
        data = await fetch_json(url, params=params)
        
        if not data or 'items' not in data:
            continue
        
        for item in data['items']:
            try:
                snippet = item.get('snippet', {})
                playlist_id = item.get('id', {}).get('playlistId')
                
                if not playlist_id:
                    continue
                
                normalized = normalize_course_data(
                    {
                        'title': snippet.get('title'),
                        'platform': 'youtube',
                        'instructor': snippet.get('channelTitle'),
                        'description': snippet.get('description', '')[:500],
                        'url': f"https://www.youtube.com/playlist?list={playlist_id}",
                        'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                        'category': 'general'
                    },
                    source='youtube'
                )
                
                normalized['hash'] = generate_course_hash(
                    normalized['title'],
                    normalized['platform']
                )
                
                courses.append(normalized)
            except Exception as e:
                logger.error(f"Error normalizing YouTube playlist: {e}")
    
    logger.info(f"Fetched {len(courses)} course playlists from YouTube")
    return courses


# ============================================
# MAIN FETCHER FUNCTION
# ============================================

async def fetch_all_courses() -> List[Dict[str, Any]]:
    """
    Fetch courses from all platforms concurrently
    
    Returns:
        List of all normalized courses
    """
    logger.info("Starting course fetch from all platforms...")
    
    # Fetch from all sources concurrently
    results = await asyncio.gather(
        fetch_classcentral(),
        fetch_udemy(),
        fetch_coursera(),
        fetch_edx(),
        fetch_freecodecamp(),
        fetch_youtube_playlists(),
        return_exceptions=True
    )
    
    # Combine all courses
    all_courses = []
    for result in results:
        if isinstance(result, list):
            all_courses.extend(result)
        elif isinstance(result, Exception):
            logger.error(f"Fetcher error: {result}")
    
    logger.info(f"Total courses fetched: {len(all_courses)}")
    return all_courses
