"""
Job Fetching Task Runner
Fetches jobs from all 12 sources
"""

import logging
from app.database import Database
from app.fetchers.job_fetcher import fetch_all_jobs
from app.utils.deduplication import deduplicate_list

logger = logging.getLogger(__name__)


async def run_job_fetcher():
    """
    Fetch jobs from all sources and store in database
    Runs every 6 hours via background scheduler
    """
    try:
        logger.info("🔄 Starting job fetch task...")
        
        # Fetch from all sources
        jobs = await fetch_all_jobs()
        
        if not jobs:
            logger.warning("⚠️  No jobs fetched")
            return
        
        # Deduplicate
        unique_jobs = deduplicate_list(jobs, hash_key='hash')
        logger.info(f"📊 Deduplicated: {len(jobs)} → {len(unique_jobs)} jobs")
        
        # Store in database
        db = Database.get_db()
        inserted_count = 0
        updated_count = 0
        
        for job in unique_jobs:
            result = await db.jobs.update_one(
                {"hash": job['hash']},
                {"$set": job},
                upsert=True
            )
            
            if result.upserted_id:
                inserted_count += 1
            elif result.modified_count > 0:
                updated_count += 1
        
        logger.info(f"✅ Job fetch complete: {inserted_count} inserted, {updated_count} updated")
        
    except Exception as e:
        logger.error(f"❌ Job fetch error: {e}")
        raise
