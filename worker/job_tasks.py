"""
Job Celery Tasks
Automated job fetching and storage
"""

from celery import shared_task
import asyncio
import logging
from datetime import datetime

from app.fetchers.job_fetcher import fetch_all_jobs
from app.database import Database
from app.utils.deduplication import deduplicate_list

logger = logging.getLogger(__name__)


@shared_task(name="worker.job_tasks.fetch_all_jobs")
def fetch_and_store_jobs():
    """
    Fetch jobs from all sources and store in MongoDB
    Runs every 6 hours via Celery beat
    """
    logger.info("Starting scheduled job fetch task...")
    
    try:
        # Run async fetcher
        jobs = asyncio.run(fetch_all_jobs())
        
        if not jobs:
            logger.warning("No jobs fetched")
            return {"status": "no_jobs", "count": 0}
        
        # Deduplicate
        unique_jobs = deduplicate_list(jobs, hash_key='hash')
        logger.info(f"Deduplicated: {len(jobs)} -> {len(unique_jobs)} jobs")
        
        # Get database
        db = Database.get_db()
        jobs_collection = db.jobs
        
        # Insert jobs (upsert based on hash)
        inserted_count = 0
        updated_count = 0
        
        for job in unique_jobs:
            result = asyncio.run(
                jobs_collection.update_one(
                    {"hash": job['hash']},
                    {"$set": job},
                    upsert=True
                )
            )
            
            if result.upserted_id:
                inserted_count += 1
            elif result.modified_count > 0:
                updated_count += 1
        
        logger.info(f"Job fetch complete: {inserted_count} inserted, {updated_count} updated")
        
        return {
            "status": "success",
            "fetched": len(jobs),
            "unique": len(unique_jobs),
            "inserted": inserted_count,
            "updated": updated_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in job fetch task: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@shared_task(name="worker.job_tasks.cleanup_expired_jobs")
def cleanup_expired_jobs():
    """
    Cleanup expired jobs (TTL should handle this, but this is a backup)
    """
    logger.info("Cleaning up expired jobs...")
    
    try:
        db = Database.get_db()
        
        result = asyncio.run(
            db.jobs.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
        )
        
        logger.info(f"Deleted {result.deleted_count} expired jobs")
        
        return {
            "status": "success",
            "deleted": result.deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up jobs: {e}")
        return {"status": "error", "error": str(e)}
