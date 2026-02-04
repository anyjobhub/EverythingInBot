"""
EverythingInBot - Main Application Entry Point
FastAPI + Aiogram 3.x Telegram Bot
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

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


# Initialize bot
bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Get dispatcher
dp = get_dispatcher()


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
        
        # Start background scheduler AFTER webhook is ready (delayed)
        logger.info("⏳ Scheduling background tasks (delayed start)...")
        asyncio.create_task(delayed_scheduler_start())
        
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


async def delayed_scheduler_start():
    """
    Start scheduler after 10 second delay
    This prevents startup load crashes and ensures webhook is ready
    """
    await asyncio.sleep(10)
    
    logger.info("🔄 Starting background scheduler...")
    from app.scheduler import scheduler
    from app.tasks import run_job_fetcher, run_course_fetcher, run_cleanup
    
    # Schedule tasks
    scheduler.add_task(run_job_fetcher, interval_hours=6, name="Job Fetcher")
    scheduler.add_task(run_course_fetcher, interval_hours=6, name="Course Fetcher")
    scheduler.add_task(run_cleanup, interval_hours=24, name="Cleanup")
    
    # Start scheduler in background (don't await - let it run forever)
    asyncio.create_task(scheduler.run())
    logger.info("✅ Background scheduler started")


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



# ============================================
# UPTIMEROBOT HEARTBEAT ENDPOINT
# ============================================

@app.get("/uptime")
@app.head("/uptime")
async def uptime_check():
    """
    UptimeRobot heartbeat endpoint
    Keeps Render.com dyno awake by pinging every 5 minutes
    
    Supports both GET and HEAD methods (UptimeRobot uses HEAD)
    
    Returns:
        Status and timestamp
    """
    from datetime import datetime
    return {
        "status": "alive",
        "service": "EverythingInBot",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# ============================================
# WEBHOOK ENDPOINT
# ============================================

@app.post(f"{settings.TELEGRAM_WEBHOOK_PATH}/{{token}}")
async def webhook_handler(request: Request, token: str) -> Response:
    """
    Telegram Webhook Handler
    CRITICAL: Returns instantly (<1ms) to prevent Render timeout/restart
    Update processing happens in background task
    """
    # Verify token (fast check)
    if token != settings.TELEGRAM_BOT_TOKEN:
        logger.warning("❌ Invalid webhook token")
        return Response(status_code=403)
    
    # Verify secret token (fast check)
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
        logger.warning("❌ Invalid secret token")
        return Response(status_code=403)
    
    # Get update data
    try:
        update_data = await request.json()
    except Exception as e:
        logger.warning(f"⚠️ Malformed update: {e}")
        return Response(status_code=200)  # Return 200 to prevent retries
    
    # Log incoming update (minimal logging)
    update_id = update_data.get('update_id', 'unknown')
    logger.info(f"📨 Update {update_id} received")
    
    # Process update in background (NON-BLOCKING)
    # This is CRITICAL - webhook returns instantly
    asyncio.create_task(process_update(update_data))
    
    # Return 200 immediately (<1ms)
    return Response(status_code=200)


async def process_update(update_data: dict):
    """
    Process Telegram update in background
    This runs asynchronously and never blocks the webhook
    """
    try:
        # Log update type
        if 'message' in update_data:
            msg = update_data['message']
            user_id = msg.get('from', {}).get('id', 'unknown')
            text = msg.get('text', 'no text')
            logger.info(f"💬 Message from {user_id}: {text[:50]}")
        elif 'callback_query' in update_data:
            cb = update_data['callback_query']
            user_id = cb.get('from', {}).get('id', 'unknown')
            data = cb.get('data', 'no data')
            logger.info(f"🔘 Callback from {user_id}: {data}")
        
        # Feed to dispatcher
        await dp.feed_webhook_update(bot, update_data)
        logger.info("✅ Update processed")
        
    except Exception as e:
        logger.error(f"❌ Update processing error: {e}", exc_info=False)  # No stack trace spam


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
