"""
Background Task Scheduler for FastAPI
Replaces Celery with internal async scheduler
"""

import asyncio
import logging
from datetime import datetime
from typing import Callable

logger = logging.getLogger(__name__)


class BackgroundScheduler:
    """
    Internal FastAPI background task scheduler
    Runs periodic tasks without external dependencies
    """
    
    def __init__(self):
        self.tasks = []
        self.running = False
    
    def add_task(self, func: Callable, interval_hours: int, name: str):
        """Add a task to the scheduler"""
        self.tasks.append({
            'func': func,
            'interval': interval_hours * 3600,  # Convert to seconds
            'name': name,
            'last_run': None
        })
        logger.info(f"📅 Scheduled task: {name} (every {interval_hours}h)")
    
    async def run(self):
        """Run the scheduler loop"""
        self.running = True
        logger.info("🚀 Background scheduler started")
        
        while self.running:
            try:
                current_time = datetime.utcnow().timestamp()
                
                for task in self.tasks:
                    # Check if task should run
                    should_run = (
                        task['last_run'] is None or
                        (current_time - task['last_run']) >= task['interval']
                    )
                    
                    if should_run:
                        logger.info(f"▶️  Running task: {task['name']}")
                        try:
                            await task['func']()
                            task['last_run'] = current_time
                            logger.info(f"✅ Task completed: {task['name']}")
                        except Exception as e:
                            logger.error(f"❌ Task failed: {task['name']} - {e}")
                
                # Sleep for 1 minute before checking again
                await asyncio.sleep(60)
                
                await asyncio.sleep(60)
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("🛑 Background scheduler stopped")


# Global scheduler instance
scheduler = BackgroundScheduler()
