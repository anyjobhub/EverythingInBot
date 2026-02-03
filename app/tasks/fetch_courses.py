"""
Course Fetching Task Runner
Fetches courses from all 6 platforms
"""

import logging
from app.database import Database
from app.fetchers.course_fetcher import fetch_all_courses
from app.utils.deduplication import deduplicate_list

logger = logging.getLogger(__name__)


async def run_course_fetcher():
    """
    Fetch courses from all platforms and store in database
    Runs every 6 hours via background scheduler
    """
    try:
        logger.info("🔄 Starting course fetch task...")
        
        # Fetch from all platforms
        courses = await fetch_all_courses()
        
        if not courses:
            logger.warning("⚠️  No courses fetched")
            return
        
        # Deduplicate
        unique_courses = deduplicate_list(courses, hash_key='hash')
        logger.info(f"📊 Deduplicated: {len(courses)} → {len(unique_courses)} courses")
        
        # Store in database
        db = Database.get_db()
        inserted_count = 0
        updated_count = 0
        
        for course in unique_courses:
            result = await db.courses.update_one(
                {"hash": course['hash']},
                {"$set": course},
                upsert=True
            )
            
            if result.upserted_id:
                inserted_count += 1
            elif result.modified_count > 0:
                updated_count += 1
        
        logger.info(f"✅ Course fetch complete: {inserted_count} inserted, {updated_count} updated")
        
    except Exception as e:
        logger.error(f"❌ Course fetch error: {e}")
        raise
