"""
Main Application Entry Point
FastAPI + Aiogram 3.x (Webhook Mode)
Optimized for Render.com Deployment
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.config import settings, get_webhook_url
from app.database import Database
from app.redis_client import RedisClient
from app.bot.dispatcher import get_dispatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Bot instance
bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Dispatcher instance
dp: Dispatcher = get_dispatcher()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting EverythingInBot...")
    
    try:
        # Connect to databases
        await Database.connect_db()
        await RedisClient.connect_redis()
        
        # Set webhook
        webhook_url = get_webhook_url()
        await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.TELEGRAM_WEBHOOK_SECRET,
            drop_pending_updates=True
        )
        logger.info(f"✅ Webhook set to: {webhook_url}")
        
        # Get bot info
        bot_info = await bot.get_me()
        logger.info(f"✅ Bot started: @{bot_info.username}")
        
        # Start background scheduler
        from app.scheduler import scheduler
        from app.tasks import run_job_fetcher, run_course_fetcher, run_cleanup
        
        # Schedule tasks
        scheduler.add_task(run_job_fetcher, interval_hours=6, name="Job Fetcher")
        scheduler.add_task(run_course_fetcher, interval_hours=6, name="Course Fetcher")
        scheduler.add_task(run_cleanup, interval_hours=24, name="Cleanup")
        
        # Start scheduler in background
        import asyncio
        asyncio.create_task(scheduler.run())
        logger.info("✅ Background scheduler started")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down EverythingInBot...")
    
    try:
        # Stop scheduler
        from app.scheduler import scheduler
        scheduler.stop()
        
        # Delete webhook
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Close connections
        await Database.close_db()
        await RedisClient.close_redis()
        await bot.session.close()
        
        logger.info("✅ Shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# Create FastAPI app
app = FastAPI(
    title="EverythingInBot API",
    description="Telegram Super-App with 10 Feature Modules",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Telegram Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IP Tracking middleware for logging system
from app.middlewares.ip_tracking import IPTrackingMiddleware
app.add_middleware(IPTrackingMiddleware)



# ============================================
# WEBHOOK ENDPOINT
# ============================================

@app.post(f"{settings.TELEGRAM_WEBHOOK_PATH}/{{token}}")
async def webhook_handler(request: Request, token: str) -> Response:
    """
    Telegram Webhook Handler
    This endpoint receives updates from Telegram
    """
    # Verify token
    if token != settings.TELEGRAM_BOT_TOKEN:
        logger.warning(f"❌ Invalid webhook token received")
        return Response(status_code=403)
    
    # Verify secret token
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
        logger.warning(f"❌ Invalid secret token")
        return Response(status_code=403)
    
    # Process update
    try:
        update_data = await request.json()
        await dp.feed_webhook_update(bot, update_data)
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        return Response(status_code=500)


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {
        "status": "healthy",
        "service": "EverythingInBot",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "EverythingInBot API is running",
        "docs": "/docs",
        "health": "/health"
    }


# ============================================
# API ROUTERS (for Telegram Mini App)
# ============================================

# Import routers (will be created in next steps)
# from app.api.routers import auth, courses, jobs, tools, etc.

# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
# app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
# ... etc


# ============================================
# RUN APPLICATION
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    # For local development only
    # In production, use: uvicorn app.main:app
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
