"""
Celery Application for Background Tasks
Handles heavy operations for all 10 modules
"""

import os
from celery import Celery
from celery.schedules import crontab

# Get Redis URL from environment
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create Celery app
celery_app = Celery(
    "everythinginbot",
    broker=redis_url,
    backend=redis_url,
    include=["worker.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Periodic tasks (cron jobs)
celery_app.conf.beat_schedule = {
    # Daily job alerts at 9 AM
    "send-daily-job-alerts": {
        "task": "worker.tasks.send_job_alerts",
        "schedule": crontab(hour=9, minute=0),
    },
    # Daily reminders at 8 AM
    "send-daily-reminders": {
        "task": "worker.tasks.send_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
    # Cleanup old data every week
    "cleanup-old-data": {
        "task": "worker.tasks.cleanup_old_data",
        "schedule": crontab(day_of_week=0, hour=2, minute=0),
    },
}

if __name__ == "__main__":
    celery_app.start()
