"""
Bot Dispatcher Setup
Configures Aiogram dispatcher with all routers and middleware
"""

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
import os

from app.redis_client import RedisClient


def get_dispatcher() -> Dispatcher:
    """
    Create and configure Aiogram dispatcher
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Initializing Aiogram Dispatcher...")
    
    # Create Redis storage for FSM
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    storage = RedisStorage.from_url(redis_url)
    
    # Create dispatcher
    dp = Dispatcher(storage=storage)
    logger.info("✅ Dispatcher created with Redis storage")
    
    # Register security middlewares
    from app.middlewares.validation import InputValidationMiddleware
    from app.middlewares.rate_limit import RateLimitMiddleware
    from app.middlewares.spam_protection import SpamProtectionMiddleware
    from app.middlewares.ip_tracking import IPTrackingMiddleware
    
    # Apply middlewares (order matters!)
    # 1. IP Tracking (first, for logging)
    dp.message.middleware(IPTrackingMiddleware())
    dp.callback_query.middleware(IPTrackingMiddleware())
    logger.info("✅ IP Tracking middleware registered")
    
    # 2. Input Validation (sanitize inputs)
    dp.message.middleware(InputValidationMiddleware(max_length=1000))
    dp.callback_query.middleware(InputValidationMiddleware())
    logger.info("✅ Input Validation middleware registered")
    
    # 3. Spam Protection (detect abuse)
    spam_protection = SpamProtectionMiddleware(
        flood_threshold=5,      # 5 messages
        flood_window=5,         # in 5 seconds
        duplicate_threshold=3,  # 3 duplicate messages
        ban_duration=3600       # 1 hour ban
    )
    dp.message.middleware(spam_protection)
    logger.info("✅ Spam Protection middleware registered")
    
    # 4. Rate Limiting (enforce limits)
    rate_limiter = RateLimitMiddleware(
        message_limit=10,       # 10 messages per minute
        message_window=60,
        command_limit=5,        # 5 commands per minute
        command_window=60,
        callback_limit=20,      # 20 callbacks per minute
        callback_window=60
    )
    dp.message.middleware(rate_limiter)
    dp.callback_query.middleware(rate_limiter)
    logger.info("✅ Rate Limiting middleware registered")

    
    # Register routers (handlers)
    logger.info("📦 Registering routers...")
    from app.bot.handlers import (
        start, m1_ai, m2_breach, m3_courses, m4_jobs, m5_tools,
        m6_productivity, m7_devtools, m8_cybersec, m9_osint, m10_fun, admin, admin_search
    )
    
    # Register all routers
    dp.include_router(start.router)
    logger.info("✅ Registered: start.router")
    
    dp.include_router(admin.router)  # Admin commands
    logger.info("✅ Registered: admin.router")
    
    dp.include_router(admin_search.router)  # Admin search logs
    logger.info("✅ Registered: admin_search.router")
    
    dp.include_router(m1_ai.router)
    logger.info("✅ Registered: m1_ai.router")
    
    dp.include_router(m2_breach.router)
    logger.info("✅ Registered: m2_breach.router")
    
    dp.include_router(m3_courses.router)
    logger.info("✅ Registered: m3_courses.router")
    
    dp.include_router(m4_jobs.router)
    logger.info("✅ Registered: m4_jobs.router")
    
    dp.include_router(m5_tools.router)
    logger.info("✅ Registered: m5_tools.router")
    
    dp.include_router(m6_productivity.router)
    logger.info("✅ Registered: m6_productivity.router")
    
    dp.include_router(m7_devtools.router)
    logger.info("✅ Registered: m7_devtools.router")
    
    dp.include_router(m8_cybersec.router)
    logger.info("✅ Registered: m8_cybersec.router")
    
    dp.include_router(m9_osint.router)
    logger.info("✅ Registered: m9_osint.router")
    
    dp.include_router(m10_fun.router)
    logger.info("✅ Registered: m10_fun.router")
    
    logger.info("🎉 All routers registered successfully!")
    logger.info(f"📊 Total routers: 13")
    
    return dp
