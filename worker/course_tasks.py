"""
Course Celery Tasks
Automated course fetching and storage
"""

from celery import shared_task
import asyncio
import logging
from datetime import datetime

from app.fetchers.course_fetcher import fetch_all_courses
from app.database import Database
from app.utils.deduplication import deduplicate_list

logger = logging.getLogger(__name__)


@shared_task(name="worker.course_tasks.fetch_all_courses")
def fetch_and_store_courses():
    """
    Fetch courses from all platforms and store in MongoDB
    Runs every 12 hours via Celery beat
    """
    logger.info("Starting scheduled course fetch task...")
    
    try:
        # Run async fetcher
        courses = asyncio.run(fetch_all_courses())
        
        if not courses:
            logger.warning("No courses fetched")
            return {"status": "no_courses", "count": 0}
        
        # Deduplicate
        unique_courses = deduplicate_list(courses, hash_key='hash')
        logger.info(f"Deduplicated: {len(courses)} -> {len(unique_courses)} courses")
        
        # Get database
        db = Database.get_db()
        courses_collection = db.courses
        
        # Insert courses (upsert based on hash)
        inserted_count = 0
        updated_count = 0
        
        for course in unique_courses:
            result = asyncio.run(
                courses_collection.update_one(
                    {"hash": course['hash']},
                    {"$set": course},
                    upsert=True
                )
            )
            
            if result.upserted_id:
                inserted_count += 1
            elif result.modified_count > 0:
                updated_count += 1
        
        logger.info(f"Course fetch complete: {inserted_count} inserted, {updated_count} updated")
        
        return {
            "status": "success",
            "fetched": len(courses),
            "unique": len(unique_courses),
            "inserted": inserted_count,
            "updated": updated_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in course fetch task: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@shared_task(name="worker.course_tasks.cleanup_expired_courses")
def cleanup_expired_courses():
    """
    Cleanup expired courses (TTL should handle this, but this is a backup)
    """
    logger.info("Cleaning up expired courses...")
    
    try:
        db = Database.get_db()
        
        result = asyncio.run(
            db.courses.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
        )
        
        logger.info(f"Deleted {result.deleted_count} expired courses")
        
        return {
            "status": "success",
            "deleted": result.deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up courses: {e}")
        return {"status": "error", "error": str(e)}
