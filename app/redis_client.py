"""
Redis Client for FSM State Management and Caching
Using Render Key-Value Store (Redis)
"""

import os
import redis.asyncio as redis
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis Client Manager"""
    
    client: Optional[redis.Redis] = None
    
    @classmethod
    async def connect_redis(cls):
        """Connect to Render Redis"""
        try:
            redis_url = os.getenv("REDIS_URL")
            if not redis_url:
                raise ValueError("REDIS_URL environment variable not set")
            
            # Create async Redis client
            cls.client = await redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=10
            )
            
            # Test connection
            await cls.client.ping()
            logger.info("✅ Connected to Redis successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise
    
    @classmethod
    async def close_redis(cls):
        """Close Redis connection"""
        if cls.client:
            await cls.client.close()
            logger.info("Redis connection closed")
    
    @classmethod
    def get_redis(cls) -> redis.Redis:
        """Get Redis client instance"""
        if cls.client is None:
            raise RuntimeError("Redis not initialized. Call connect_redis() first.")
        return cls.client


# Convenience function for FastAPI dependency injection
async def get_redis() -> redis.Redis:
    """FastAPI dependency to get Redis client"""
    return RedisClient.get_redis()
