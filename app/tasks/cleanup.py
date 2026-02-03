"""
Cleanup Task Runner
Removes old logs and expired data
"""

import logging
from datetime import datetime, timedelta
from app.database import Database

logger = logging.getLogger(__name__)


async def run_cleanup():
    """
    Clean up old logs and expired data
    Runs every 24 hours via background scheduler
    """
    try:
        logger.info("🧹 Starting cleanup task...")
        
        db = Database.get_db()
        cutoff_date = datetime.utcnow() - timedelta(days=180)
        
        # Clean old search logs (180 days)
        result = await db.search_logs.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        logger.info(f"🗑️  Deleted {result.deleted_count} old search logs")
        
        # Clean old button clicks (180 days)
        result = await db.button_clicks.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        logger.info(f"🗑️  Deleted {result.deleted_count} old button clicks")
        
        # Clean old admin logs (180 days)
        result = await db.admin_logs.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        logger.info(f"🗑️  Deleted {result.deleted_count} old admin logs")
        
        logger.info("✅ Cleanup complete")
        
    except Exception as e:
        logger.error(f"❌ Cleanup error: {e}")
        raise
