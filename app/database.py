"""
MongoDB Database Connection using Motor (Async Driver)
Optimized for Render.com deployment with MongoDB Atlas
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """MongoDB Database Manager using Motor"""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB Atlas"""
        try:
            mongodb_uri = os.getenv("MONGODB_URI")
            if not mongodb_uri:
                raise ValueError("MONGODB_URI environment variable not set")
            
            # Create async MongoDB client
            cls.client = AsyncIOMotorClient(
                mongodb_uri,
                maxPoolSize=10,
                minPoolSize=1,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                retryWrites=True,
                w='majority'
            )
            
            # Get database
            cls.db = cls.client.everythinginbot
            
            # Test connection
            await cls.client.admin.command('ping')
            logger.info("✅ Connected to MongoDB Atlas successfully")
            
            # Create indexes
            await cls.create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")
    
    @classmethod
    async def create_indexes(cls):
        """Create database indexes for performance"""
        try:
            # Users collection indexes
            await cls.db.users.create_index("telegram_id", unique=True)
            await cls.db.users.create_index("tier")
            await cls.db.users.create_index("created_at")
            
            # Subscriptions collection indexes
            await cls.db.subscriptions.create_index([("user_id", 1), ("status", 1)])
            await cls.db.subscriptions.create_index("expires_at")
            
            # Courses collection indexes
            await cls.db.courses.create_index("category")
            await cls.db.courses.create_index("published")
            await cls.db.courses.create_index([("category", 1), ("published", 1)])
            
            # Jobs collection indexes
            await cls.db.jobs.create_index([("category", 1), ("location", 1)])
            await cls.db.jobs.create_index("posted_at")
            await cls.db.jobs.create_index("active")
            
            # User progress collection indexes
            await cls.db.user_progress.create_index(
                [("user_id", 1), ("course_id", 1)], 
                unique=True
            )
            
            # Tool usage collection indexes
            await cls.db.tool_usage.create_index([("user_id", 1), ("tool_name", 1)])
            await cls.db.tool_usage.create_index("timestamp")
            
            # OSINT history indexes
            await cls.db.osint_history.create_index("user_id")
            await cls.db.osint_history.create_index("timestamp")
            
            # Breach checks indexes
            await cls.db.breach_checks.create_index("user_id")
            await cls.db.breach_checks.create_index("email")
            
            # Analytics indexes
            await cls.db.analytics.create_index("event_type")
            await cls.db.analytics.create_index("timestamp")
            
            # Search logs indexes (NEW - for logging system)
            await cls.db.search_logs.create_index("telegram_id")
            await cls.db.search_logs.create_index("timestamp")
            await cls.db.search_logs.create_index("module_name")
            await cls.db.search_logs.create_index([("telegram_id", 1), ("timestamp", -1)])
            await cls.db.search_logs.create_index([("telegram_id", 1), ("module_name", 1)])
            
            # Jobs collection indexes (NEW - for automated job fetching)
            await cls.db.jobs.create_index("hash", unique=True)  # Deduplication
            await cls.db.jobs.create_index("expires_at", expireAfterSeconds=0)  # TTL index (24 hours)
            await cls.db.jobs.create_index("category")
            await cls.db.jobs.create_index("country")
            await cls.db.jobs.create_index("type")
            await cls.db.jobs.create_index([("posted_at", -1)])  # Latest first
            await cls.db.jobs.create_index([("category", 1), ("country", 1)])
            
            # Courses collection indexes (NEW - for automated course fetching)
            await cls.db.courses.create_index("hash", unique=True)  # Deduplication
            await cls.db.courses.create_index("expires_at", expireAfterSeconds=0)  # TTL index (48 hours)
            await cls.db.courses.create_index("category")
            await cls.db.courses.create_index("platform")
            await cls.db.courses.create_index("difficulty")
            await cls.db.courses.create_index("language")
            await cls.db.courses.create_index([("category", 1), ("platform", 1)])
            
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
            # Don't raise - indexes are optimization, not critical
    
    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if cls.db is None:
            raise RuntimeError("Database not initialized. Call connect_db() first.")
        return cls.db


# Convenience function for FastAPI dependency injection
async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency to get database"""
    return Database.get_db()


# Collection shortcuts
def get_users_collection():
    """Get users collection"""
    return Database.get_db().users


def get_subscriptions_collection():
    """Get subscriptions collection"""
    return Database.get_db().subscriptions


def get_courses_collection():
    """Get courses collection"""
    return Database.get_db().courses


def get_jobs_collection():
    """Get jobs collection"""
    return Database.get_db().jobs


def get_tool_usage_collection():
    """Get tool usage collection"""
    return Database.get_db().tool_usage


def get_analytics_collection():
    """Get analytics collection"""
    return Database.get_db().analytics


def get_search_logs_collection():
    """Get search logs collection"""
    return Database.get_db().search_logs


# Alias for backward compatibility
async def get_db() -> AsyncIOMotorDatabase:
    """Get database instance (async alias)"""
    return Database.get_db()
